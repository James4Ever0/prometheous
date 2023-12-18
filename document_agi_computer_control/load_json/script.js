fetch('./demo.json')
    .then(response => {
        console.log(response); // not found?
        // response.json();
        // console.log(body);
        // return response.body;
        return response.json();
    }
    )
    .then(data => {
        console.log(data);
        document.getElementById('title').textContent = data.title;
        document.getElementById('description').textContent = data.description;
    })
    .catch(error => {
        console.error('Error loading JSON:', error);
    });
