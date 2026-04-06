// Authentication JavaScript for Toonify AI

// Switch between Sign In and Sign Up tabs
function switchAuthTab(tab) {
    const signinForm = document.getElementById('signin-form');
    const signupForm = document.getElementById('signup-form');
    const signinBtn = document.getElementById('signin-tab-btn');
    const signupBtn = document.getElementById('signup-tab-btn');

    if (tab === 'signin') {
        signinForm.classList.remove('hidden');
        signupForm.classList.add('hidden');
        signinBtn.classList.add('border-purple-600', 'text-white');
        signinBtn.classList.remove('border-transparent', 'text-gray-400');
        signupBtn.classList.remove('border-purple-600', 'text-white');
        signupBtn.classList.add('border-transparent', 'text-gray-400');
    } else {
        signupForm.classList.remove('hidden');
        signinForm.classList.add('hidden');
        signupBtn.classList.add('border-purple-600', 'text-white');
        signupBtn.classList.remove('border-transparent', 'text-gray-400');
        signinBtn.classList.remove('border-purple-600', 'text-white');
        signinBtn.classList.add('border-transparent', 'text-gray-400');
    }
}

// Scroll to auth section
function scrollToAuth() {
    const authSection = document.getElementById('auth-section');
    authSection.scrollIntoView({ behavior: 'smooth' });
}

// Password strength indicator
const signupPassword = document.getElementById('signup-password');
if (signupPassword) {
    signupPassword.addEventListener('input', function () {
        const password = this.value;
        const strengthBar = document.getElementById('password-strength-bar');
        const strengthText = document.getElementById('password-strength-text');

        let strength = 0;
        let color = 'bg-red-500';
        let text = 'Weak';

        // Calculate strength
        if (password.length >= 8) strength += 25;
        if (password.match(/[a-z]/)) strength += 25;
        if (password.match(/[A-Z]/)) strength += 25;
        if (password.match(/[0-9]/)) strength += 15;
        if (password.match(/[^a-zA-Z0-9]/)) strength += 10;

        // Set color and text based on strength
        if (strength >= 75) {
            color = 'bg-green-500';
            text = 'Strong';
        } else if (strength >= 50) {
            color = 'bg-yellow-500';
            text = 'Medium';
        } else if (strength >= 25) {
            color = 'bg-orange-500';
            text = 'Fair';
        }

        // Update UI
        strengthBar.style.width = strength + '%';
        strengthBar.className = `h-full ${color} rounded-full transition-all duration-300`;
        strengthText.textContent = text;
        strengthText.className = `text-xs ${color.replace('bg-', 'text-')}`;
    });
}

// Handle Sign In
async function handleSignIn() {
    const username = document.getElementById('signin-username').value;
    const password = document.getElementById('signin-password').value;

    if (!username || !password) {
        showToast('Please fill in all fields', 'error');
        return;
    }

    try {
        // Create form data
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        // Make API request
        const response = await fetch('http://localhost:8000/auth/login/form', {
            method: 'POST',
            body: formData,
        });

        const data = await response.json();

        if (response.ok) {
            // Store token
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('token_type', data.token_type);

            showToast('Sign in successful! Redirecting...', 'success');

            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1500);
        } else {
            showToast(data.detail || 'Sign in failed', 'error');
        }
    } catch (error) {
        console.error('Sign in error:', error);
        showToast('Network error. Please try again.', 'error');
    }
}

// Handle Sign Up
async function handleSignUp() {
    const email = document.getElementById('signup-email').value;
    const username = document.getElementById('signup-username').value;
    const fullname = document.getElementById('signup-fullname').value;
    const password = document.getElementById('signup-password').value;
    const confirmPassword = document.getElementById('signup-confirm-password').value;

    // Validation
    if (!email || !username || !password || !confirmPassword) {
        showToast('Please fill in all required fields', 'error');
        return;
    }

    if (password !== confirmPassword) {
        showToast('Passwords do not match', 'error');
        return;
    }

    if (password.length < 8) {
        showToast('Password must be at least 8 characters', 'error');
        return;
    }

    try {
        // Make API request
        const response = await fetch('http://localhost:8000/auth/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                username: username,
                full_name: fullname || username,
                password: password,
            }),
        });

        const data = await response.json();

        if (response.ok) {
            showToast('Account created successfully! Please sign in.', 'success');

            // Switch to sign in tab
            setTimeout(() => {
                switchAuthTab('signin');
                document.getElementById('signin-username').value = username;
            }, 1500);
        } else {
            showToast(data.detail || 'Sign up failed', 'error');
        }
    } catch (error) {
        console.error('Sign up error:', error);
        showToast('Network error. Please try again.', 'error');
    }
}

// Toast notification function
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');

    const toast = document.createElement('div');
    toast.className = `toast px-6 py-4 rounded-xl shadow-2xl backdrop-blur-xl border z-50 ${type === 'success' ? 'bg-green-500/90 border-green-400' :
        type === 'error' ? 'bg-red-500/90 border-red-400' :
            'bg-blue-500/90 border-blue-400'
        }`;
    toast.textContent = message;

    container.appendChild(toast);

    // Remove after 3 seconds
    setTimeout(() => {
        toast.classList.add('removing');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Handle Enter key press
document.addEventListener('DOMContentLoaded', function () {
    const signinUsername = document.getElementById('signin-username');
    const signinPassword = document.getElementById('signin-password');

    if (signinUsername && signinPassword) {
        signinUsername.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') handleSignIn();
        });

        signinPassword.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') handleSignIn();
        });
    }

    const signupConfirmPassword = document.getElementById('signup-confirm-password');
    if (signupConfirmPassword) {
        signupConfirmPassword.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') handleSignUp();
        });
    }
});
