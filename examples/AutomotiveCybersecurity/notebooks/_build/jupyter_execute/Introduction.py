# Introduction: How H1st.AI enables the Industrial AI Revolution

This tutorial will teach you how H1st AI can help solve the Cold Start problem in domains where labeled data is not available or prohibitively expensive to obtain.

One example of such a domain is cybersecurity, which is increasingly looking forward to adopting ML to detect intrusions. Another domain is predictive maintenance that tries to anticipate industrial machine failures before they happen. In both domains, labels are expensive because fundamentally these occurrences are rare and costly (as compared to NLP where e.g. sentiment are common and labels can be obtained i.g. via crowdsourcing or weak supervision).
Yet this is a fundamental challenge of Industrial AI.

<img src="http://docs.arimo.com/H1ST_AI_Tutorial/img/batman h1st.ai.jpg" alt="H1st.AI woke meme" style="float: left; margin-right: 20px; margin-bottom: 20px;" width=320px height=320px>

Jurgen Schmidhuber, one of AI & deep learning's pioneer, [remarked in his 2020s outlook that](http://people.idsia.ch/~juergen/2010s-our-decade-of-deep-learning.html#Sec.%207) in the last decade AI "excelled in virtual worlds, e.g., in video games, board games, and especially on the major WWW platforms", but the main challenge for the next decades is for AI to be "driving industrial processes and machines and robots".

As pioneers in Industrial AI who regularly work with massive global fleets of IoT equipment, Arimo & Panasonic whole-heartedly agrees with this outlook. Importantly, many industrial AI use cases with significant impact have become urgent and demand solutions now that requires a fresh approach. We will work on one such example in this tutorial: detection intrusion in automotive cybersecurity.

We’ll learn that using H1st.AI we can tackle these problems and make it tractable by leveraging human experience and data-driven models in a harmonious way. Especially, we’ll learn how to:

  * Perform use-case analysis to decompose problems and adopt different models at the right level of abstractions
  * Encode human experience as a model
  * Combine human and ML models to work in tandem in a H1st.Graph
    
Too many tutorials, esp data science ones, start out with some toy applications and the really basic stuff, and then stalls out on the more complex real-world scenario. This one is going to be different. 

So, grab a cup of coffee before you continue :)

If you can't wait, go ahead and [star our Github repository](https://github.com/h1st-ai/h1st) and check out the "Quick Start" section. We're open-source!


```{toctree}
:hidden:
:titlesonly:


Automotive Cybersecurity - A Cold Start Problem.ipynb
Monolithic AD & ML Approaches and Why They are Unsatisfactory.ipynb
Using H1st.AI to Encode Human Insights as a Model and Harmonize Human + ML in a H1st.Graph.ipynb
Summary & Further Resources
```
