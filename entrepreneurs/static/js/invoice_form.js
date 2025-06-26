document.addEventListener('DOMContentLoaded', function() {
    const addButton = document.getElementById('add-item');
    const container = document.getElementById('items-container');
    const totalForms = document.getElementById('id_form-TOTAL_FORMS');
    
    addButton.addEventListener('click', function() {
        const formCount = parseInt(totalForms.value);
        const newForm = document.querySelector('.item-form').cloneNode(true);
        

        const formRegex = /form-(\d+)-/g;
        newForm.innerHTML = newForm.innerHTML.replace(formRegex, `form-${formCount}-`);
        

        newForm.querySelectorAll('input').forEach(input => {
            if (input.type !== 'hidden' && input.name !== 'form-__prefix__-DELETE') {
                input.value = '';
            }
        });
        
        container.appendChild(newForm);
        totalForms.value = formCount + 1;
    });
});