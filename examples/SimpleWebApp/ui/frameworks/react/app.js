import React from 'react';

const App = function() {

    const [uploaded, setUploaded] = React.useState(false);

    const uploadModel = async () => {
        const file = ""; // obtain file
        await fetch('/execute_model', 'POST', {
            file: file
        })
    }

    return (
        <div>
            <h1>Upload your model</h1>
            <input type="file" name="model_id" /> 
            <button onClick={uploadModel}>Submit</button>

            { uploaded && (
                <h2>File upload successfully</h2>
            )}
        </div>
    )
}

export default App;