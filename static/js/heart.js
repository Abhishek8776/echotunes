function wish(h1,h2) {
    const img1=document.getElementById(h1)
    const img2=document.getElementById(h2)
    img1.classList.add('d-none')
    img2.classList.toggle('d-block')
}