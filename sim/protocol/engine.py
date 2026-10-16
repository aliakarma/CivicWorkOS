"""Reference execution of the CivicWorkOS evaluation protocol.

A day-stepped synthetic municipal testbed with three service domains
(structural inspection, street maintenance and sanitation, citizen-service
casework). Each domain has certified practitioners, trainee posts, and a
fleet of robots or a pool of AI agents. Latent quantities the allocator must
learn -- each practitioner's current proficiency, each fleet's reliability,
each domain's task requirement, each practitioner's workload response --
evolve or are drawn per seed, and are observed only through task outcomes
and, where available, multimodal signals (skill probes, fleet telemetry,
physiological workload estimates).

Five policies run on identical exogenous streams (common random numbers):
every arrival, requirement, outcome draw, fault draw, sensor reading,
attrition time and machine-reliability path is fixed by the seed and the
scenario, so policy comparisons are paired.

* ``static``: a fixed allocation table set at commissioning from prior
  ratings; trainees accompany human-involved work when free; no learning.
* ``efficiency``: per-task maximization of immediate expected value on
  learned estimates, with no capability, retention, workload or oversight
  terms.
* ``civicworkos``: the same estimates and objective plus the capability
  budget with catch-up admissibility, periodic human-led tasks, a workload
  ceiling on multimodal estimates, uncertainty- and consequence-gated
  oversight, and readiness-constrained control transfer.
* ``civicworkos_nolearn`` and ``civicworkos_noretention``: ablations.

Nothing produced here is a measurement of any city. It is a reproducible
software demonstration that the specified mechanisms behave as the article
claims under the stated assumptions.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from .config import POLICY_FLAGS, SCENARIOS, DomainSpec, ModeSpec, PolicyFlags, RunConfig, Scenario, SimParams
from .estimation import adf_bernoulli, kalman_scalar, lower_confidence_success, predictive_success, sigmoid
from .skill import asymptotic_proficiency, current_proficiency, recency_interval

SUPERVISION_RECOVERY = 0.75   # share of the lead--trainee proficiency gap a supervising lead recovers
MAX_ATTEMPTS = 8
POOL_PER_DOMAIN = 64
U_OUTCOME, U_FAULT, U_TAKEOVER, U_INCIDENT, U_PROBE = range(5)


# --------------------------------------------------------------------------
# Exogenous world: everything a seed and a scenario fix, shared by policies.
# --------------------------------------------------------------------------

@dataclass
class World:
    seed: int
    scenario: Scenario
    task_day: np.ndarray        # arrival day per task
    task_dom: np.ndarray        # domain index per task
    task_req: np.ndarray        # true requirement b_i per task
    task_cons: np.ndarray       # consequential flag per task
    task_u: np.ndarray          # (n_tasks, MAX_ATTEMPTS, 5) uniforms
    task_z: np.ndarray          # (n_tasks, MAX_ATTEMPTS, 3) standard normals for probes
    machine_rel: np.ndarray     # (n_domains, days) true fleet reliability
    telemetry_ok: np.ndarray    # (n_domains, days) bool
    telemetry_z: np.ndarray     # (n_domains, days) normals
    pool: list[list[dict]]      # per-domain practitioner pool attributes
    sensor_u: np.ndarray        # (n_domains, POOL, days) uniforms
    sensor_z: np.ndarray        # (n_domains, POOL, days) normals


def make_world(seed: int, scenario: Scenario, cfg: RunConfig) -> World:
    P, D = cfg.params, cfg.domains
    rng = np.random.default_rng([seed, 7919])
    days = P.days
    t_day, t_dom, t_req, t_cons = [], [], [], []
    for d in range(days):
        surge = scenario.surge_factor if scenario.surge_start <= d < scenario.surge_start + scenario.surge_days else 1.0
        for k, spec in enumerate(D):
            n = rng.poisson(spec.arrivals_per_day * surge)
            for _ in range(n):
                t_day.append(d)
                t_dom.append(k)
                t_req.append(spec.requirement + spec.requirement_sd * rng.standard_normal())
                t_cons.append(rng.random() < spec.consequential_share)
    n_tasks = len(t_day)
    task_u = rng.random((n_tasks, MAX_ATTEMPTS, 5))
    task_z = rng.standard_normal((n_tasks, MAX_ATTEMPTS, 3))

    machine_rel = np.empty((len(D), days))
    for k, spec in enumerate(D):
        x = spec.machine_reliability
        for d in range(days):
            x = spec.machine_reliability + P.machine_reversion * (x - spec.machine_reliability) \
                + P.machine_drift_sd * rng.standard_normal()
            in_disruption = scenario.disruption_start <= d < scenario.disruption_start + scenario.disruption_days
            machine_rel[k, d] = scenario.disruption_reliability if in_disruption else x
    telemetry_ok = rng.random((len(D), days)) < P.telemetry_prob
    telemetry_z = rng.standard_normal((len(D), days))

    pool: list[list[dict]] = []
    for k, spec in enumerate(D):
        members = []
        for j in range(POOL_PER_DOMAIN):
            initial = j < spec.n_certified
            members.append({
                "c": spec.h_k * rng.uniform(1.6, 2.6) if initial else spec.h_k * rng.uniform(0.0, 0.5),
                "gap": float(rng.integers(0, 10)) if initial else 0.0,
                "rate_mult": float(np.exp(P.rate_cv * rng.standard_normal() - 0.5 * P.rate_cv ** 2)),
                "tau": P.tau_ret * float(np.exp(P.tau_ret_cv * rng.standard_normal() - 0.5 * P.tau_ret_cv ** 2)),
                "load_mult": float(max(0.6, 1.0 + P.load_sd * rng.standard_normal())),
                "exit_after": float(rng.exponential(P.days_per_year / spec.attrition_per_year)),
            })
        pool.append(members)
    sensor_u = rng.random((len(D), POOL_PER_DOMAIN, days))
    sensor_z = rng.standard_normal((len(D), POOL_PER_DOMAIN, days))
    return World(seed, scenario, np.array(t_day), np.array(t_dom), np.array(t_req), np.array(t_cons, dtype=bool),
                 task_u, task_z, machine_rel, telemetry_ok, telemetry_z, pool, sensor_u, sensor_z)


# --------------------------------------------------------------------------
# Endogenous state.
# --------------------------------------------------------------------------

@dataclass
class Practitioner:
    slot: int                   # index into the domain pool (pairs hires across policies)
    c: float
    gap: float
    rate_mult: float
    tau: float
    load_mult: float
    exit_after: float
    certified_day: int | None
    active: bool = True
    off_m: float = 0.0          # belief: proficiency offset from the nominal model
    off_v: float = 0.0
    load_m: float = 1.0         # belief: workload response multiplier
    load_v: float = 0.0
    hours: float = 0.0
    demand: float = 0.0
    led_today: bool = False


@dataclass
class Metrics:
    arrived: int = 0
    completed: int = 0
    arrived_w: int = 0
    completed_w: int = 0
    cost: float = 0.0
    human_days: int = 0
    overload_days: int = 0
    load_sum: float = 0.0
    takeover_requests: int = 0
    takeover_success: int = 0
    takeover_requests_w: int = 0
    takeover_success_w: int = 0
    takeover_time_sum: float = 0.0
    takeover_time_n: int = 0
    mrc: int = 0
    incidents: int = 0
    trainee_credit: float = 0.0
    retention_reservations: int = 0
    oversight_routings: int = 0
    relaxations: int = 0
    graduations: int = 0
    trajectory: list = field(default_factory=list)


class Run:
    """One policy on one world."""

    def __init__(self, world: World, policy: str, cfg: RunConfig):
        self.w, self.policy, self.cfg = world, policy, cfg
        self.P: SimParams = cfg.params
        self.D: tuple[DomainSpec, ...] = cfg.domains
        self.F: PolicyFlags = POLICY_FLAGS[policy]
        P = self.P
        self.pract: list[list[Practitioner]] = []
        self.next_slot: list[int] = []
        for k, spec in enumerate(self.D):
            people = []
            for j in range(spec.n_certified + spec.n_trainee_posts):
                people.append(self._hire(k, j, certified_day=0 if j < spec.n_certified else None))
            self.pract.append(people)
            self.next_slot.append(spec.n_certified + spec.n_trainee_posts)
        self.mach_m = [d.machine_reliability for d in self.D]
        self.mach_v = [P.machine_prior_var for _ in self.D]
        self.req_m = [d.requirement + d.requirement_prior_bias for d in self.D]
        self.req_v = [P.requirement_prior_var for _ in self.D]
        self.lam = [0.0 for _ in self.D]
        self.M = Metrics()
        self.attempts = np.zeros(len(world.task_day), dtype=np.int16)
        self.mach_left = [0.0 for _ in self.D]

    # ---- people -----------------------------------------------------------
    def _hire(self, k: int, slot: int, certified_day: int | None) -> Practitioner:
        a = self.w.pool[k][slot]
        return Practitioner(slot=slot, c=a["c"], gap=a["gap"], rate_mult=a["rate_mult"], tau=a["tau"],
                            load_mult=a["load_mult"], exit_after=a["exit_after"], certified_day=certified_day,
                            off_v=self.P.prior_offset_var, load_v=self.P.load_sd ** 2)

    def certified(self, k: int, p: Practitioner) -> bool:
        return p.active and p.c >= self.D[k].h_k

    def theta_true(self, k: int, p: Practitioner) -> float:
        P = self.P
        inf = asymptotic_proficiency(p.c, self.D[k].h_k, P.theta_0, P.theta_comp, p.rate_mult)
        return current_proficiency(inf, p.gap, p.tau, P.residual)

    def theta_nominal(self, k: int, p: Practitioner) -> float:
        P = self.P
        inf = asymptotic_proficiency(p.c, self.D[k].h_k, P.theta_0, P.theta_comp)
        return current_proficiency(inf, p.gap, P.tau_ret, P.residual)

    def theta_est(self, k: int, p: Practitioner) -> float:
        return self.theta_nominal(k, p) + (p.off_m if self.F.learning else 0.0)

    def load_est(self, p: Practitioner) -> float:
        return p.load_m if self.F.learning else 1.0

    def recency_need(self, k: int, p: Practitioner) -> float:
        """Gap as a share of the estimated recency interval (1.0 means lapsing now).

        The interval is evaluated on the nominal learning curve, whose
        asymptote the practice log determines; the learned offset already
        contains any decay, so it enters the readiness test of the lead
        (``theta_est``) rather than this clock.
        """
        P = self.P
        inf = asymptotic_proficiency(p.c, self.D[k].h_k, P.theta_0, P.theta_comp)
        dmax = recency_interval(inf, P.tau_ret, P.residual, P.theta_comp)
        return math.inf if dmax <= 0.0 else p.gap / dmax

    def hours_cap(self) -> float:
        return self.P.avail_h * self.P.overtime_factor

    def fits(self, p: Practitioner, hours: float, demand: float) -> bool:
        if p.hours + hours > self.hours_cap() + 1e-9:
            return False
        if self.F.workload_guard:
            P = self.P
            if (p.demand + demand) * self.load_est(p) > P.workload_margin * P.workload_ceiling * P.avail_h:
                return False
        return True

    # ---- prediction -------------------------------------------------------
    def team_coefs(self, mode: ModeSpec, trainee: bool) -> tuple[float, float]:
        """Weights of lead and trainee proficiency in the team's human proficiency."""
        if not trainee:
            return 1.0, 0.0
        wt = self.P.omega_trainee * (1.0 - SUPERVISION_RECOVERY)
        return 1.0 - wt, wt

    def predict(self, k: int, mode: ModeSpec, lead: Practitioner | None, tr: Practitioner | None):
        """Mean and variance of the linear predictor, and its belief components."""
        phi = mode.phi
        means, vars_, coefs = [], [], []
        offset = 0.0
        if lead is not None:
            cl, ct = self.team_coefs(mode, tr is not None)
            offset += phi * cl * self.theta_nominal(k, lead)
            means.append(lead.off_m if self.F.learning else 0.0)
            vars_.append(lead.off_v)
            coefs.append(phi * cl)
            if tr is not None:
                offset += phi * ct * self.theta_nominal(k, tr)
                means.append(tr.off_m if self.F.learning else 0.0)
                vars_.append(tr.off_v)
                coefs.append(phi * ct)
        if mode.machine:
            offset += (1.0 - phi) * mode.machine_bonus
            means.append(self.mach_m[k])
            vars_.append(self.mach_v[k])
            coefs.append(1.0 - phi)
        means.append(self.req_m[k])
        vars_.append(self.req_v[k])
        coefs.append(-1.0)
        m = offset + sum(a * x for a, x in zip(coefs, means))
        v = sum(a * a * s for a, s in zip(coefs, vars_))
        return m, v, means, vars_, coefs, offset

    def true_z(self, k: int, mode: ModeSpec, lead, tr, day: int, req: float) -> float:
        phi = mode.phi
        z = -req
        if lead is not None:
            cl, ct = self.team_coefs(mode, tr is not None)
            th = cl * self.theta_true(k, lead) + (ct * self.theta_true(k, tr) if tr is not None else 0.0)
            z += phi * th
        if mode.machine:
            z += (1.0 - phi) * (self.w.machine_rel[k, day] + mode.machine_bonus)
        return z

    # ---- decision ---------------------------------------------------------
    def choose(self, k: int, ti: int, day: int):
        P, spec, F = self.P, self.D[k], self.F
        people = self.pract[k]
        certs = [p for p in people if self.certified(k, p)]
        trainees = [p for p in people if p.active and not self.certified(k, p)]
        risk_crit = spec.risk * spec.crit
        p_min = 0.55 + 0.35 * risk_crit
        req_hours = spec.duration_h
        due = []
        if F.retention:
            due = sorted((p for p in certs if self.recency_need(k, p) >= P.retention_guard
                          and self.theta_est(k, p) >= P.theta_comp),
                         key=lambda p: (-self.recency_need(k, p), p.slot))

        # HCPB catch-up quantities (eq. catchup of the article)
        year_day = day % P.days_per_year
        n_cert = len(certs)
        budget = P.eta * n_cert * spec.attrition_per_year * spec.h_k
        trajectory = budget * (year_day + 1) / P.days_per_year
        remaining = max(1.0, spec.arrivals_per_day * (P.days_per_year - year_day))
        catchup = max(0.0, budget - self.lam[k]) / remaining
        behind = F.capability_terms and self.lam[k] < trajectory

        cands = []
        for mode in spec.modes:
            hours = req_hours * mode.duration_mult
            if mode.machine and self.mach_left[k] < hours - 1e-9:
                continue
            demand = hours * mode.demand
            if mode.phi == 0.0:
                rosters = [(None, None)]
            else:
                leads = [p for p in certs if self.fits(p, hours, demand)]
                if not leads:
                    continue
                if self.policy == "static":
                    lead = min(leads, key=lambda p: (p.hours, p.slot))
                else:
                    lead = max(leads, key=lambda p: (self.theta_est(k, p), -p.slot))
                leads_tried = [lead]
                if F.retention and due:
                    # periodic human-led tasks: also offer the most overdue current practitioner
                    due_fit = [p for p in due if self.fits(p, hours, demand)]
                    if due_fit and due_fit[0] is not lead:
                        leads_tried.append(due_fit[0])
                free_tr = [p for p in trainees if self.fits(p, hours, demand)]
                tr = min(free_tr, key=lambda p: (p.hours, p.slot)) if free_tr else None
                rosters = []
                for ld in leads_tried:
                    rosters.append((ld, None))
                    if tr is not None:
                        rosters.append((ld, tr))
                if F.retention and self.theta_est(k, lead) >= P.theta_comp:
                    # supervised refresher: a lapsed certified practitioner, once a day, beside a current lead
                    lapsed = [p for p in leads if p is not lead and not p.led_today
                              and self.theta_est(k, p) < P.theta_comp]
                    if lapsed:
                        ref = max(lapsed, key=lambda p: (self.theta_est(k, p), -p.slot))
                        rosters.append((lead, ref))
            for lead, tr in rosters:
                m, v, *_ = self.predict(k, mode, lead, tr)
                p_hat = predictive_success(m, v, P.gamma)
                p_chk = lower_confidence_success(m, v, P.gamma) if F.capability_terms else p_hat
                if self.policy == "static":
                    p_chk = p_hat
                if p_chk < p_min:
                    continue
                oversight_block = False
                if F.oversight and mode.phi == 0.0:
                    p_sd = p_hat * (1.0 - p_hat) * P.gamma * math.sqrt(v)
                    if self.w.task_cons[ti] or p_sd > P.oversight_p_sd:
                        oversight_block = True
                wage = 0.0
                if lead is not None:
                    wage += hours * P.wage_certified
                if tr is not None:
                    wage += hours * (P.wage_certified if self.certified(k, tr) else P.wage_trainee)
                cost = wage + (hours * spec.machine_cost_per_h if mode.machine else 0.0)
                ev = P.value * (0.5 + 0.5 * spec.crit) * p_hat - cost \
                    - P.incident_cost * P.p_incident_failure * spec.risk * (1.0 - p_hat)
                ell = spec.learn * hours
                second = P.omega_trainee if tr is not None else 0.0
                refresher = tr is not None and self.certified(k, tr)
                credit = 0.0 if refresher else ell * mode.phi * second
                led_ok = lead is not None and mode.phi * (1.0 - second) >= P.human_led_share
                restores = refresher and mode.phi * second >= P.human_led_share
                cands.append({"mode": mode, "lead": lead, "tr": tr, "ev": ev, "credit": credit,
                              "oversight_block": oversight_block, "led_ok": led_ok,
                              "due_lead": bool(due) and lead is not None and lead is due[0],
                              "restores": restores})
        if not cands:
            return None

        if self.policy == "static":
            fixed = [c for c in cands if c["mode"].name == spec.static_mode]
            pool = fixed if fixed else cands
            with_tr = [c for c in pool if c["tr"] is not None]
            pick = (with_tr or pool)[0] if pool else None
            return pick

        admissible = [c for c in cands if not c["oversight_block"]]
        if F.oversight and len(admissible) < len(cands) and not admissible:
            self.M.oversight_routings += 1
            return None
        if F.oversight and any(c["oversight_block"] for c in cands):
            self.M.oversight_routings += 1
        stages = [admissible]
        if F.capability_terms and behind and any(c["credit"] > 0.0 for c in admissible):
            cap_ok = [c for c in admissible if c["credit"] >= catchup - 1e-12]
            stages.insert(0, cap_ok)
        if F.retention:
            ret_first = [c for c in stages[0]
                         if (due and c["due_lead"] and c["led_ok"]) or c["restores"]]
            stages.insert(0, ret_first)
        for i, s in enumerate(stages):
            if s:
                pick = max(s, key=lambda c: c["ev"])
                if F.retention and i == 0:
                    self.M.retention_reservations += 1
                if i == len(stages) - 1 and len(stages) > 1:
                    self.M.relaxations += 1
                return pick
        return None

    # ---- takeover ---------------------------------------------------------
    def sa_multiplier(self, k: int, p: Practitioner, extra_demand: float, true: bool) -> float:
        P = self.P
        th = self.theta_true(k, p) if true else self.theta_est(k, p)
        lm = p.load_mult if true else self.load_est(p)
        mult = 1.0 + 3.0 * max(0.0, 0.9 - th)
        if p.gap > P.ootl_days:
            mult *= 1.0 + P.ootl_factor
        if (p.demand + extra_demand) * lm / P.avail_h > 0.9:
            mult *= P.overload_sa_factor
        return mult

    def pick_takeover(self, k: int, hours: float) -> Practitioner | None:
        P, spec = self.P, self.D[k]
        certs = [p for p in self.pract[k] if self.certified(k, p)]
        if not certs:
            return None
        demand = hours * 1.5
        if self.policy == "static":
            return min(certs, key=lambda p: (p.hours, p.slot))
        b = self.req_m[k]
        if not self.F.readiness_takeover:
            return max(certs, key=lambda p: (self.theta_est(k, p), -p.slot))
        ready = []
        for p in certs:
            sd = math.sqrt(p.off_v)
            if self.theta_est(k, p) - P.readiness_z * sd < P.theta_comp:
                continue
            if (p.demand + demand) * self.load_est(p) > P.takeover_headroom * P.workload_ceiling * P.avail_h:
                continue
            t_est = P.t_detect + P.t_reach + P.t_sa * self.sa_multiplier(k, p, demand, true=False)
            if t_est > spec.takeover_budget_min:
                continue
            ready.append(p)
        if not ready:
            return None
        return max(ready, key=lambda p: (sigmoid(P.gamma * (self.theta_est(k, p) - b)), -p.slot))

    # ---- execution --------------------------------------------------------
    def execute(self, k: int, ti: int, day: int, pick: dict, window: bool) -> bool:
        P, spec, F, M = self.P, self.D[k], self.F, self.M
        mode, lead, tr = pick["mode"], pick["lead"], pick["tr"]
        hours = spec.duration_h * mode.duration_mult
        att = min(int(self.attempts[ti]), MAX_ATTEMPTS - 1)
        self.attempts[ti] += 1
        u = self.w.task_u[ti, att]
        zs = self.w.task_z[ti, att]
        req = float(self.w.task_req[ti])
        demand = hours * mode.demand
        for p in (lead, tr):
            if p is not None:
                p.hours += hours
                p.demand += demand
        if mode.machine:
            self.mach_left[k] -= hours
        cost = 0.0
        if lead is not None:
            cost += hours * P.wage_certified
        if tr is not None:
            cost += hours * (P.wage_certified if self.certified(k, tr) else P.wage_trainee)
        if mode.machine:
            cost += hours * spec.machine_cost_per_h

        # practice credit and the recency clock
        ell = spec.learn * hours
        psi = P.omega_trainee if tr is not None else 0.0
        if lead is not None:
            lead.c += ell * mode.phi * (1.0 - psi)
            if mode.phi * (1.0 - psi) >= P.human_led_share:
                lead.led_today = True
        if tr is not None:
            if not self.certified(k, tr):     # developmental credit counts toward the budget
                self.lam[k] += ell * mode.phi * psi
                M.trainee_credit += ell * mode.phi * psi
            tr.c += ell * mode.phi * psi
            if mode.phi * psi >= P.human_led_share:
                tr.led_today = True

        in_disruption = (self.w.scenario.disruption_start <= day
                         < self.w.scenario.disruption_start + self.w.scenario.disruption_days)
        fault_rate = self.w.scenario.disruption_fault_rate if in_disruption else P.fault_rate
        success = False
        if mode.machine and u[U_FAULT] < fault_rate:
            M.takeover_requests += 1
            if window:
                M.takeover_requests_w += 1
            if F.learning:   # a fault is evidence about the fleet
                mm, vv = adf_bernoulli([self.mach_m[k]], [self.mach_v[k]], [1.0],
                                       mode.machine_bonus - self.req_m[k], False, P.gamma)
                self.mach_m[k], self.mach_v[k] = mm[0], vv[0]
            if lead is not None:
                taker, t_reach = lead, 0.0
                sa = self.sa_multiplier(k, lead, 0.0, true=True) * 0.5
            else:
                taker = self.pick_takeover(k, hours)
                t_reach = P.t_reach
                sa = self.sa_multiplier(k, taker, hours * 0.75, true=True) if taker is not None else 0.0
            if taker is None:
                M.mrc += 1
                if u[U_INCIDENT] < P.p_incident_mrc * spec.risk:
                    M.incidents += 1
                    cost += P.incident_cost
            else:
                t = P.t_detect + t_reach + P.t_sa * sa
                if lead is None:
                    taker.hours += 0.5 * hours
                    taker.demand += 0.75 * hours
                    taker.led_today = True
                    taker.c += ell * 0.5
                    cost += 0.5 * hours * P.wage_certified
                th = self.theta_true(k, taker)
                overloaded = taker.demand * taker.load_mult / P.avail_h > P.workload_ceiling
                p_to = sigmoid(P.gamma * (th - req)) * (0.7 if overloaded else 1.0)
                ok = t <= spec.takeover_budget_min and u[U_TAKEOVER] < p_to
                M.takeover_time_sum += t
                M.takeover_time_n += 1
                if F.learning and t <= spec.takeover_budget_min:
                    mm, vv = adf_bernoulli([taker.off_m, self.req_m[k]], [taker.off_v, self.req_v[k]], [1.0, -1.0],
                                           self.theta_nominal(k, taker), ok, P.gamma)
                    taker.off_m, self.req_m[k] = mm
                    taker.off_v, self.req_v[k] = vv
                if ok:
                    success = True
                    M.takeover_success += 1
                    if window:
                        M.takeover_success_w += 1
                elif u[U_INCIDENT] < P.p_incident_takeover_failure * spec.risk:
                    M.incidents += 1
                    cost += P.incident_cost
        else:
            z = self.true_z(k, mode, lead, tr, day, req)
            success = u[U_OUTCOME] < sigmoid(P.gamma * z)
            if not success and u[U_INCIDENT] < P.p_incident_failure * spec.risk:
                M.incidents += 1
                cost += P.incident_cost
            if F.learning:
                _, _, means, vars_, coefs, offset = self.predict(k, mode, lead, tr)
                nm, nv = adf_bernoulli(means, vars_, coefs, offset, success, P.gamma)
                j = 0
                for p in (lead, tr):
                    if p is not None:
                        p.off_m, p.off_v = nm[j], nv[j]
                        j += 1
                if mode.machine:
                    self.mach_m[k], self.mach_v[k] = nm[j], nv[j]
                    j += 1
                self.req_m[k], self.req_v[k] = nm[j], nv[j]
        # multimodal skill probes (learning policies only, where available)
        if F.learning and u[U_PROBE] < P.probe_prob:
            for idx, p in enumerate((lead, tr)):
                if p is not None:
                    obs = self.theta_true(k, p) + P.probe_sd * zs[idx]
                    m_new, v_new = kalman_scalar(p.off_m, p.off_v, obs - self.theta_nominal(k, p), P.probe_sd ** 2)
                    p.off_m, p.off_v = m_new, v_new
        M.cost += cost
        return success

    # ---- main loop --------------------------------------------------------
    def run(self) -> Metrics:
        P, D, w, F, M = self.P, self.D, self.w, self.F, self.M
        sc = w.scenario
        win = sc.window()
        order = np.argsort(w.task_day, kind="stable")
        ptr = 0
        queue: list[int] = []
        n_tasks = len(w.task_day)
        for day in range(P.days):
            # machines: capacity, belief prediction, telemetry
            in_disruption = sc.disruption_start <= day < sc.disruption_start + sc.disruption_days
            for k, spec in enumerate(D):
                cap = spec.machine_units * P.machine_h_per_unit
                self.mach_left[k] = cap * (sc.disruption_capacity if in_disruption else 1.0)
                if F.learning:
                    self.mach_v[k] += P.machine_process_var
                    if w.telemetry_ok[k, day]:
                        obs = w.machine_rel[k, day] + P.telemetry_sd * w.telemetry_z[k, day]
                        self.mach_m[k], self.mach_v[k] = kalman_scalar(self.mach_m[k], self.mach_v[k], obs,
                                                                       P.telemetry_sd ** 2)
                if day % P.days_per_year == 0:
                    self.lam[k] = 0.0
                for p in self.pract[k]:
                    p.hours = p.demand = 0.0
                    p.led_today = False
                    if F.learning:
                        p.off_v += P.human_process_var
            # arrivals
            while ptr < n_tasks and w.task_day[order[ptr]] == day:
                ti = int(order[ptr])
                queue.append(ti)
                M.arrived += 1
                if win and win[0] <= day < win[1]:
                    M.arrived_w += 1
                ptr += 1
            queue.sort(key=lambda t: (w.task_day[t] + D[w.task_dom[t]].deadline_days, -D[w.task_dom[t]].risk, t))
            pending = []
            for ti in queue:
                k = int(w.task_dom[ti])
                pick = self.choose(k, ti, day)
                arrived_in_win = bool(win and win[0] <= w.task_day[ti] < win[1])
                done = False
                if pick is not None:
                    done = self.execute(k, ti, day, pick, window=bool(win and win[0] <= day < win[1]))
                if done:
                    M.completed += 1
                    if arrived_in_win:
                        M.completed_w += 1
                elif day < w.task_day[ti] + D[k].deadline_days and self.attempts[ti] < MAX_ATTEMPTS:
                    pending.append(ti)
            queue = pending
            # end of day: workload, sensors, recency, certification, attrition
            for k, spec in enumerate(D):
                people = self.pract[k]
                for p in people:
                    if not p.active:
                        continue
                    index = p.demand * p.load_mult / P.avail_h
                    M.human_days += 1
                    M.load_sum += index
                    if index > P.workload_ceiling:
                        M.overload_days += 1
                    if F.learning and p.demand > 0.5 and w.sensor_u[k, p.slot, day] < P.workload_sensor_prob:
                        obs = p.load_mult + P.workload_sensor_sd * w.sensor_z[k, p.slot, day]
                        p.load_m, p.load_v = kalman_scalar(p.load_m, p.load_v, obs, P.workload_sensor_sd ** 2)
                    p.gap = 0.0 if p.led_today else p.gap + 1.0
                    if p.certified_day is None and p.c >= spec.h_k:
                        p.certified_day = day
                        M.graduations += 1
                        if self.next_slot[k] < POOL_PER_DOMAIN:
                            people.append(self._hire(k, self.next_slot[k], None))
                            self.next_slot[k] += 1
                    if p.certified_day is not None and day >= p.certified_day + p.exit_after:
                        p.active = False
            if day % 5 == 4 or day == P.days - 1:
                M.trajectory.append((day + 1, *self.snapshot()))
        return M

    def snapshot(self) -> tuple[int, int, float]:
        n_cert = n_curr = 0
        prof = 0.0
        for k in range(len(self.D)):
            for p in self.pract[k]:
                if self.certified(k, p):
                    n_cert += 1
                    th = self.theta_true(k, p)
                    prof += th
                    if th >= self.P.theta_comp:
                        n_curr += 1
        return n_cert, n_curr, (prof / n_cert if n_cert else float("nan"))


def run_one(seed: int, scenario_name: str, policy: str, cfg: RunConfig | None = None) -> dict:
    cfg = cfg or RunConfig()
    world = make_world(seed, SCENARIOS[scenario_name], cfg)
    r = Run(world, policy, cfg)
    M = r.run()
    n_cert, n_curr, prof = r.snapshot()
    return {
        "seed": seed, "scenario": scenario_name, "policy": policy,
        "completion_rate": M.completed / max(M.arrived, 1),
        "completion_rate_window": (M.completed_w / M.arrived_w) if M.arrived_w else float("nan"),
        "cost_per_completed": M.cost / max(M.completed, 1),
        "overload_share": M.overload_days / max(M.human_days, 1),
        "mean_workload": M.load_sum / max(M.human_days, 1),
        "certified_end": n_cert,
        "current_end": n_curr,
        "current_share_end": n_curr / n_cert if n_cert else float("nan"),
        "mean_proficiency_end": prof,
        "takeover_requests": M.takeover_requests,
        "takeover_success_rate": M.takeover_success / M.takeover_requests if M.takeover_requests else float("nan"),
        "takeover_success_window": (M.takeover_success_w / M.takeover_requests_w) if M.takeover_requests_w
        else float("nan"),
        "takeover_requests_window": M.takeover_requests_w,
        "takeover_time_mean": M.takeover_time_sum / M.takeover_time_n if M.takeover_time_n else float("nan"),
        "mrc": M.mrc,
        "incidents_per_1000": 1000.0 * M.incidents / max(M.arrived, 1),
        "trainee_credit_per_year": M.trainee_credit * cfg.params.days_per_year / cfg.params.days,
        "graduations": M.graduations,
        "retention_reservations": M.retention_reservations,
        "oversight_routings": M.oversight_routings,
        "relaxations": M.relaxations,
        "arrived": M.arrived,
        "trajectory": M.trajectory,
    }
