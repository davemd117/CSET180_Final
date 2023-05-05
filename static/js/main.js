function openAddProduct() {
    document.getElementById("add_product_popup").style.display = "block";
}

function closeAddProduct() {
    document.getElementById("add_product_popup").style.display = "none";
}

function openAddVariant() {
    document.getElementById("add_variant_popup").style.display = "block";
}

function closeAddVariant() {
    document.getElementById("add_variant_popup").style.display = "none";
}

function openUpdateProduct() {
    document.getElementById("update_product_popup").style.display = "block";
}

function closeUpdateProduct() {
    document.getElementById("update_product_popup").style.display = "none";
}

const update_variant_form = document.querySelectorAll(".update_variant_popup");
const update_variant_button = document.querySelectorAll(".update_variant_button");
const close_update_variant_button = document.querySelectorAll(".close_update_variant_button");

update_variant_button.forEach((button, index) => {
    button.addEventListener("click", () => {
        update_variant_form[index].classList.remove("update_variant_popup_hidden");
        update_variant_form[index].classList.add("update_variant_popup_visible");
    });
});

close_update_variant_button.forEach((button, index) => {
    button.addEventListener("click", () => {
        update_variant_form[index].classList.remove("update_variant_popup_visible");
        update_variant_form[index].classList.add("update_variant_popup_hidden");
    });
});