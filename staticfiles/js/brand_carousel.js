let brandCarousel = document.querySelector('.carousel.brand-carousel'); 

let items = brandCarousel.querySelectorAll('.carousel-item.brand-slide');

		items.forEach((el) => {
			const minPerSlide = 5
			let next = el.nextElementSibling
			for (var i=1; i<minPerSlide; i++) {
				if (!next) {
            next = items[0]
        }
        let cloneChild = next.cloneNode(true)
        el.appendChild(cloneChild.children[0])
        next = next.nextElementSibling
    }
})