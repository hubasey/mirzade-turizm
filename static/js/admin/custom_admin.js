// Mirzade Turizm Admin Panel Özel JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Admin paneli yüklendiğinde çalışacak kodlar
    console.log('Mirzade Turizm Admin Panel yüklendi');
    
    // Sayfa yüklendiğinde animasyon ekle
    document.body.classList.add('loaded');
    
    // Form alanlarına otomatik odaklanma
    const firstInput = document.querySelector('.form-row input:not([type=hidden]):not([readonly])');
    if (firstInput) {
        firstInput.focus();
    }
    
    // Hata mesajlarını daha belirgin hale getir
    const errorList = document.querySelector('ul.errorlist');
    if (errorList) {
        errorList.classList.add('animated-error');
        // Sayfayı hata mesajına doğru kaydır
        errorList.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    // Tablo satırlarına hover efekti ekle
    const tableRows = document.querySelectorAll('#result_list tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f5f5f5';
            this.style.transition = 'background-color 0.3s ease';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });
    
    // Uzun form sayfalarında hızlı gezinme için "Yukarı Çık" butonu ekle
    if (document.querySelector('form')) {
        const backToTopButton = document.createElement('button');
        backToTopButton.innerHTML = '&#8679;'; // Yukarı ok işareti
        backToTopButton.className = 'back-to-top';
        backToTopButton.title = 'Yukarı Çık';
        backToTopButton.style.position = 'fixed';
        backToTopButton.style.bottom = '20px';
        backToTopButton.style.right = '20px';
        backToTopButton.style.width = '40px';
        backToTopButton.style.height = '40px';
        backToTopButton.style.borderRadius = '50%';
        backToTopButton.style.backgroundColor = '#00927E';
        backToTopButton.style.color = 'white';
        backToTopButton.style.border = 'none';
        backToTopButton.style.fontSize = '20px';
        backToTopButton.style.cursor = 'pointer';
        backToTopButton.style.display = 'none';
        backToTopButton.style.zIndex = '1000';
        backToTopButton.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
        
        document.body.appendChild(backToTopButton);
        
        backToTopButton.addEventListener('click', function() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
        
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopButton.style.display = 'block';
            } else {
                backToTopButton.style.display = 'none';
            }
        });
    }
    
    // Tarih seçicileri için iyileştirmeler
    const dateInputs = document.querySelectorAll('.vDateField');
    dateInputs.forEach(input => {
        input.setAttribute('placeholder', 'GG.AA.YYYY');
    });
    
    // Zaman seçicileri için iyileştirmeler
    const timeInputs = document.querySelectorAll('.vTimeField');
    timeInputs.forEach(input => {
        input.setAttribute('placeholder', 'SS:DD');
    });
    
    // Dosya yükleme alanları için önizleme
    const imageInputs = document.querySelectorAll('input[type=file]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && file.type.match('image.*')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    // Mevcut önizlemeyi kaldır
                    const existingPreview = input.parentNode.querySelector('.image-preview');
                    if (existingPreview) {
                        existingPreview.remove();
                    }
                    
                    // Yeni önizleme oluştur
                    const preview = document.createElement('div');
                    preview.className = 'image-preview';
                    preview.style.marginTop = '10px';
                    preview.style.maxWidth = '300px';
                    
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.style.maxWidth = '100%';
                    img.style.borderRadius = '4px';
                    img.style.boxShadow = '0 2px 5px rgba(0,0,0,0.1)';
                    
                    preview.appendChild(img);
                    input.parentNode.appendChild(preview);
                }
                reader.readAsDataURL(file);
            }
        });
    });
}); 