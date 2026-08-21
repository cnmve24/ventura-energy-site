(function(){
  var els = document.querySelectorAll('.rise');
  function revealAll(){ els.forEach(function(el){ el.classList.add('in'); }); }

  if ('IntersectionObserver' in window) {
    document.documentElement.classList.add('js-anim');
    var io = new IntersectionObserver(function(es){
      es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); } });
    }, {rootMargin:'0px 0px -8% 0px', threshold:.06});
    els.forEach(function(el){ io.observe(el); });
    // failsafe: if the observer never delivers (throttled tab, odd viewer),
    // show everything rather than leaving the page blank
    setTimeout(revealAll, 2500);
  }

  // resiliency slider: native scroll-snap, so touch swipe works for free.
  // Buttons and dots update state directly rather than waiting on the scroll
  // event, so navigation stays responsive while a smooth scroll is still running.
  var track=document.getElementById('resilSlides');
  if (track) {
    var slides=track.children,
        dots=document.getElementById('resilDots'),
        capEl=document.getElementById('resilCap'),
        prev=document.querySelector('.sl-prev'),
        next=document.querySelector('.sl-next'),
        current=0;

    for (var i=0;i<slides.length;i++) {
      (function(n){
        var b=document.createElement('button');
        b.className='sl-dot'; b.type='button';
        b.setAttribute('aria-label','Photo '+(n+1)+' of '+slides.length);
        b.addEventListener('click', function(){ go(n); });
        dots.appendChild(b);
      })(i);
    }

    function render(n){
      current=n;
      capEl.textContent=(n+1)+' / '+slides.length+'  '+(slides[n].dataset.cap||'');
      for (var i=0;i<dots.children.length;i++){
        dots.children[i].setAttribute('aria-current', i===n ? 'true' : 'false');
      }
      prev.disabled = n===0;
      next.disabled = n===slides.length-1;
    }

    function go(n){
      n=Math.max(0, Math.min(slides.length-1, n));
      render(n);
      track.scrollTo({left: n*track.clientWidth, behavior:'smooth'});
    }

    prev.addEventListener('click', function(){ go(current-1); });
    next.addEventListener('click', function(){ go(current+1); });
    track.addEventListener('keydown', function(e){
      if (e.key==='ArrowRight'){ e.preventDefault(); go(current+1); }
      if (e.key==='ArrowLeft'){ e.preventDefault(); go(current-1); }
    });

    // manual swipe or trackpad scroll: settle, then adopt whatever slide we landed on
    var t=null;
    track.addEventListener('scroll', function(){
      clearTimeout(t);
      t=setTimeout(function(){
        var n=Math.round(track.scrollLeft/track.clientWidth);
        n=Math.max(0, Math.min(slides.length-1, n));
        if (n!==current) render(n);
      }, 110);
    }, {passive:true});

    window.addEventListener('resize', function(){
      track.scrollTo({left: current*track.clientWidth, behavior:'auto'});
    });

    render(0);
  }

  var lb=document.getElementById('lb'), img=document.getElementById('lb-img'), cap=document.getElementById('lb-cap');
  document.querySelectorAll('.shot').forEach(function(b){
    b.addEventListener('click', function(){
      var t=b.querySelector('img');
      img.src=t.src; img.alt=t.alt; cap.textContent=b.dataset.cap || '';
      lb.showModal();
    });
  });
  document.getElementById('lb-close').addEventListener('click', function(){ lb.close(); });
  lb.addEventListener('click', function(e){ if(e.target===lb) lb.close(); });
})();
