hamburger_button = document.querySelector("#hamburger")
hamburger_menu = document.querySelector("#hamburger_menu")

hamburger = () =>{
    if (hamburger_menu.style.opacity == 1) {
        hamburger_menu.style.opacity = 0
        hamburger_menu.style.width = "0vw"
    }
    else{
        hamburger_menu.style.opacity = 1;
        hamburger_menu.style.width = "100vw";
    }
}