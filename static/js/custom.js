// static/js/custom.js
document.addEventListener('DOMContentLoaded', function() {
    console.log('Custom JS loaded!'); // Debug line

    // Handle login required modal
    const loginRequiredModal = document.getElementById('loginRequiredModal');

    if (loginRequiredModal) {
        console.log('Modal element found!'); // Debug line

        loginRequiredModal.addEventListener('show.bs.modal', function(event) {
            console.log('Modal show event triggered!'); // Debug line

            const button = event.relatedTarget;
            const courseTitle = button.getAttribute('data-course-title');

            console.log('Course title:', courseTitle); // Debug line

            const modalTitle = loginRequiredModal.querySelector('#modalCourseTitle');
            if (modalTitle && courseTitle) {
                modalTitle.textContent = courseTitle;
                console.log('Modal title updated!'); // Debug line
            }
        });
    } else {
        console.log('Modal element NOT found!'); // Debug line
    }

    // Debug: Check if Bootstrap is loaded
    if (typeof bootstrap !== 'undefined') {
        console.log('✅ Bootstrap is loaded!');
        console.log('✅ Modal component:', bootstrap.Modal);
    } else {
        console.log('❌ Bootstrap is NOT loaded!');
    }
});