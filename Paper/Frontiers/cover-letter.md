Dear Editors of Frontiers in Neurorobotics,

We submit the manuscript *CivicWorkOS: Capability-Preserving Adaptive Task Allocation Among Humans, AI Agents, and Robots in Municipal Services* as a **Methods** article for the Research Topic *Data-driven Neurorobotics: Multimodal Learning, Adaptive Intelligence, and Reproducible Human–Robot Interaction* (Topic Editors: Huyong Yan, Jie Yang, Di Wu, and Zhong Chen). The main text is 9,572 words, with 4 figures and 9 tables; a Supplementary Material document carries the full protocol, extended results, proofs, and the legal and data-protection analysis.

Municipal services increasingly divide work among public employees, AI agents, and robots. Allocating that work for immediate efficiency removes the practice through which people stay able to supervise machines, handle exceptions, and take over when automation fails. The manuscript proposes an adaptive allocation method that treats human proficiency as a changing resource. It learns task requirements, practitioner proficiency, machine reliability, and workload response from task outcomes and, where available, multimodal observations (skill probes, robot telemetry, and physiological workload estimates). It also protects supervised practice and periodic human-led work within workload limits, and it transfers control of a failing machine only to a practitioner who is ready to take over.

The submission fits the Research Topic in three ways. It is a learning-based adaptive method for human–robot–AI teams whose estimates are interpretable by construction. Its central contribution is a **reproducible evaluation protocol**, with three service domains, five policies, three scenarios, and eight hypotheses fixed before the evaluation code was written. And its reference execution over 30 paired seeds is regenerated, number by number, by one command from the openly released software (https://github.com/aliakarma/CivicWorkOS).

We report the evaluation as it came out. Four of the eight pre-specified hypotheses are supported: capability-preserving allocation keeps 27.5 practitioners current at the end of three years against 9.6 under efficiency-focused allocation, certifies 10.9 new practitioners against none, and keeps workload overload at 0.04% of practitioner-days against 4.18%. Four are not supported. Preservation costs 1.73 times as much per completed task, routine completion falls by 1.6 points, takeover success does not reach its pre-specified margin, and learning lowers task completion during an automation disruption even as it cuts incidents roughly sixfold. Exploratory analyses show that the multimodal channels are what make the learning work: learning from task outcomes alone produces proficiency estimates worse than not learning at all. The testbed is synthetic and its parameters illustrative, which the manuscript states wherever results appear.

The manuscript is not under consideration elsewhere, and all authors have approved its submission. The authors declare no competing interests.

Sincerely,

Raghda M. Alqurashi (corresponding author), on behalf of all authors
Department of Computer Science, Umm Al-Qura University
rmqurashi@uqu.edu.sa
