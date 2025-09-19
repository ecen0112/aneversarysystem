// Preview uploaded image
function previewImage(event) {
    const preview = document.getElementById('preview');
    const file = event.target.files[0];
    if (file) {
        preview.src = URL.createObjectURL(file);
        preview.style.display = 'block';
    } else {
        preview.style.display = 'none';
    }
}

// Like button toggle with floating heart
function toggleLike(btn) {
    btn.classList.toggle('liked');
    const text = btn.querySelector('.like-text');
    text.textContent = btn.classList.contains('liked') ? 'Liked!' : 'Like';

    if (btn.classList.contains('liked')) {
        createFloatingHeart(btn);
    }
}

// Create floating heart animation
function createFloatingHeart(element) {
    const heart = document.createElement("span");
    heart.innerHTML = "&#10084;";
    heart.classList.add("floating-heart");

    // Place heart relative to button
    const rect = element.getBoundingClientRect();
    heart.style.left = rect.left + rect.width / 2 + "px";
    heart.style.top = rect.top - 20 + "px";

    document.body.appendChild(heart);

    setTimeout(() => {
        heart.remove();
    }, 2000);
}

// Navbar shadow on scroll
window.addEventListener("scroll", () => {
    const navbar = document.querySelector(".navbar");
    if (window.scrollY > 50) {
        navbar.classList.add("scrolled");
    } else {
        navbar.classList.remove("scrolled");
    }
});

// Typing effect for hero title (only once on load)
document.addEventListener("DOMContentLoaded", () => {
    const heroTitle = document.querySelector(".hero-anniversary h1");
    if (heroTitle) {
        const text = heroTitle.textContent.trim();
        heroTitle.textContent = "";
        let i = 0;

        function typingEffect() {
            if (i < text.length) {
                heroTitle.textContent += text.charAt(i);
                i++;
                setTimeout(typingEffect, 100);
            }
        }
        typingEffect();
    }
});

// Falling background hearts
function createBackgroundHeart() {
    const heart = document.createElement("span");
    heart.innerHTML = "&#10084;";
    heart.classList.add("floating-heart");

    const size = Math.random() * 20 + 10;
    heart.style.fontSize = size + "px";
    heart.style.position = "fixed";
    heart.style.left = Math.random() * 100 + "vw";
    heart.style.top = "-20px";
    heart.style.animation = "floatUp 4s linear forwards";

    document.querySelector(".animated-hearts").appendChild(heart);

    setTimeout(() => {
        heart.remove();
    }, 4000);
}

// Spawn hearts every 1s
setInterval(createBackgroundHeart, 1000);
