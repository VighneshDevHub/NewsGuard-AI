// NavBar.js - Handles navbar functionality

document.addEventListener('DOMContentLoaded', function() {
    const hamburgerMenu = document.querySelector('.hamburger-menu');
    const sidebar = document.querySelector('.sidebar');
    const backIcon = document.querySelector('.back-icon');
    const overlay = document.querySelector('.overlay');

    // Toggle sidebar when hamburger menu is clicked
    if (hamburgerMenu) {
        hamburgerMenu.addEventListener('click', function() {
            sidebar.classList.add('active');
            overlay.style.display = 'block';
            document.body.style.overflow = 'hidden';
        });
    }

    // Close sidebar when back icon is clicked
    if (backIcon) {
        backIcon.addEventListener('click', function() {
            sidebar.classList.remove('active');
            overlay.style.display = 'none';
            document.body.style.overflow = 'auto';
        });
    }

    // Close sidebar when overlay is clicked
    if (overlay) {
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('active');
            overlay.style.display = 'none';
            document.body.style.overflow = 'auto';
        });
    }
    
    // Profile Dropdown Functionality
    const profileToggle = document.getElementById('profileDropdownToggle');
    const profileDropdown = document.getElementById('profileDropdown');
    
    // Toggle dropdown when clicking the profile icon
    if (profileToggle && profileDropdown) {
        profileToggle.addEventListener('click', function(e) {
            e.preventDefault();
            profileDropdown.classList.toggle('show');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!profileToggle.contains(e.target) && !profileDropdown.contains(e.target)) {
                profileDropdown.classList.remove('show');
            }
        });
    }
});
