# Summary & Further Resources

That was a long tutorial! But hey, when was the last time you've seen a non-trivial one?

To recap, the H1ST.AI principles & ideas we've learned:
  * Leverage use-case analysis to decompose problems and adopt different models at the right level of abstractions
  * Encoding human experience as a model
  * Combine human experience and data-driven insights to work harmoniously in a H1st Graph

Most importantly, we have used H1ST.AI to tackle a real-world challenging automotive cybersecurity problem, for which attack event labels are not available to start with, hence solving the Cold Start problem. 

It is important to stress that this is still a toy example IDS and much more is needed to handle attacks (e.g. replacement attacks where a whole ECU can be compromised & normal messages silenced and there won’t be a zig-zag pattern) and of course on-device vs cloud deployment, OTA updates, etc. But it is clear adopting H1ST.AI makes the problem much more tractable and explainable.

H1ST.AI framework further provides productivity tools for a team of Data Scientists and domain experts to collaborate on such complex software projects. Especially, we’ve seen our own productivity vastly when moving from a spaghetti code jungle of ML to a more principled H1ST project structure and make use of H1ST Model API & repository as well as Graph.

Excited? [Star/fork our Github repo](https://github.com/h1st-ai/h1st), we're open-source! Especially check out the "Quick Start" section.