==================
Knowledge-First AI
==================

Why Knowledge-First
===================

An ML-only approach to enterprise AI would fail to leverage the abundant human expertise that is available, and sometimes even necessary, for industrial applications. Knowledge-First AI embraces the codification and automation of knowledge and intelligence from any source, including and especially human knowledge and expertise.

This approach makes it possible to build and deploy AI systems even before there is sufficient data for machine learning. Across the industry, lack of data for machine learning is a widespread issue. It is important to be able (a) to leverage and automate human expertise that is already available, and (b) to combine it with machine-learned models as data and labels become more available over time.

.. image:: eie-diagram.jpg
  :width: 700px
  :align: center
  :alt: Encoding Integration Ensembling

Knowledge First AI aims to streamline the combination of Human and Machine Intelligence in diverse ways.

Encoding Human Knowledge: The Oracle
====================================

Over the last decades, in each domain of industry, human experts have been playing a significant role in the operation of industrial companies. These experts have accumulated knowledge and know-how within specific domains and can provide a foundational understanding to solve domain-specific problems.

However, human knowledge is limited as it is hard to encode, store, and transfer within an organization. This is where machine learning has a distinct advantage: generalization. But to build a machine learning model, sufficient data is needed.

**The Oracle** allows AI teams to leverage expert knowledge already present in an organization and combine that knowledge with machine learning to (a) provide immediate system functionality without sufficient data for ML, and (b) scale up and generalize system functionality as data becomes more available. This approach solves a fundamental problem for starting an AI projects -- insufficient data -- and unblocks application development around the ML components. Moreover, even when the ML components are fully operational, the additional expert feedback can be used to improve, or even modify, AI performance.

**How it works**

An **Oracle** is a predictive node composed of 3 main components: a **Teacher**, a **Student** and an **Ensemble**.

The **Teacher** is a model that caputres domain-specific expert knowledge through rules and logic. Acting upon unlabeled data, the **Teacher** generates predictions which can be used to operational functionality, but also these predictions act as labels for training the **Student** -- an ML model which will eventually generalize the expert knowledge codified within the **Teacher**. The **Ensemble** model collects predictions from both the **Teacher** and the **Student** to render a final decision. The **Ensemble** can operate through simple logic or, if sufficent data exists, can be implemented with ML. Together these system comprise an **Oracle**. This setup is illustrated in the diagram below. In practice, it is simple to create and use an **Oracle**, and a basic example is laid out in the Quick-start guide. 

  .. image:: h1st-oracle.jpg
    :width: 522px
    :align: center
    :alt: H1st Oracle Architecture


