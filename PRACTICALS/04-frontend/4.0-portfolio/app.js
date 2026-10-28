// Dark Mode Toggle
const toggleBtn = document.getElementById('themeToggle');
const html = document.documentElement;

toggleBtn.addEventListener('click', () => {
    html.classList.toggle('dark');
    if (html.classList.contains('dark')) {
        toggleBtn.textContent = '🌙 Dark';
        document.body.classList.add('bg-gray-900', 'text-white');
        document.body.classList.remove('bg-white', 'text-black');
    } else {
        toggleBtn.textContent = '☀️ Light';
        document.body.classList.remove('bg-gray-900', 'text-white');
        document.body.classList.add('bg-white', 'text-black');
    }
});

// Contact Form (fake submit)
const form = document.getElementById('contactForm');
const status = document.getElementById('formStatus');

form.addEventListener('submit', (e) => {
    e.preventDefault();
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const message = document.getElementById('message').value;
    
    console.log('Form submitted:', { name, email, message });
    
    status.classList.remove('hidden');
    form.reset();
    
    setTimeout(() => status.classList.add('hidden'), 3000);
});
