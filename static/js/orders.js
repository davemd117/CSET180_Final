const review_form = document.querySelectorAll(".review_popup_container");
const open_review_btn = document.querySelectorAll(".open_review_btn");
const close_review_btn = document.querySelectorAll(".close_review_btn");

open_review_btn.forEach((button, index) => {
    button.addEventListener("click", () => {
        review_form[index].classList.remove("review_popup_hidden");
        review_form[index].classList.add("review_popup_visible");
    });
});

close_review_btn.forEach((button, index) => {
    button.addEventListener("click", () => {
        review_form[index].classList.remove("review_popup_visible");
        review_form[index].classList.add("review_popup_hidden");
    });
});

const complaint_form = document.querySelectorAll(".complaint_popup_container");
const open_complaint_btn = document.querySelectorAll(".open_complaint_btn");
const close_complaint_btn = document.querySelectorAll(".close_complaint_btn");

open_complaint_btn.forEach((button, index) => {
    button.addEventListener("click", () => {
        complaint_form[index].classList.remove("complaint_popup_hidden");
        complaint_form[index].classList.add("complaint_popup_visible");
    });
});

close_complaint_btn.forEach((button, index) => {
    button.addEventListener("click", () => {
        complaint_form[index].classList.remove("complaint_popup_visible");
        complaint_form[index].classList.add("complaint_popup_hidden");
    });
});