from h1st.model import model

if __name__ == "__main__":
    m = model.Model()
    print(m.predict({"x": 1}))
    print(m.predict({"x": 0}))