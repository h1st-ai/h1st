Knowledge-First AI
==================

Over the last decades, in each domain of industry, human experts have been playing a significant role in the operation of industrial companies. These experts have accumulated knowledge and know-how on a specific domain and can provide a foundation understanding to solve domain-specific problems.

However, human knowledge has its limit as it is hard to generalize and hard to transfer within an organization. This is where machine learning has its advantage. But to build a machine learning model, sufficient data is needed.

Knowledge-First AI approach allows AI team (a) to leverage and automate human expertise that is already available, and (b) to combine it with machine-learned models as data and labels become more available over time. This approach solves the fundamental problem for starting an AI project: insufficient data. Moreover, additional experts' feedback can be used to improve AI performance.

**How it works**

  We started by capturing expert knowledge into what we call **The Teacher** - a model that encodes the expert rule in a specific domain. We will use **The Teacher** and unlabeled data to generate labeled data and to train **The Student** - an ML model that generalizes the expert rules. Finally, we will ensemble these prediction result into **The Oracle**. The diagram below shows the described technique.

  .. image:: h1st-oracle.jpg
    :width: 522px
    :align: center
    :alt: H1st Oracle Architecture


**Oracle**

  In practical building and using the Oracle is much simpler. You build an Oracle as follows:

  .. code-block:: python

      from h1st.oracle.example.datasets import load_oracle_tutorial_data
      from h1st.oracle.example.teacher import DefaultTeacherModel
      from h1st.oracle.oracle import Oracle

      # For better tutorial, we provide example data and k_model
      df = load_oracle_tutorial_data() # pd.read_csv('data_path')
      my_k_model = DefaultTeacherModel()

      # Instantiate oracle
      oracle = Oracle()
      oracle.build(
          data={'X': df}
          knowledge_model=my_k_model
      )
      oracle.persist('my_oracle_v1')


  
  And you can use the Oracle as follows:

  .. code-block:: python

      from h1st.oracle.oracle import Oracle
      my_oracle = Oracle().load('my_oracle_v1')
      my_oracle.predict(data)



