async g=>{localStorage.removeItem('arxgames-v1');__games.play(g);const P=__games.puzzle(g);
 if(g==='ladder'){for(let t=0;t<3;t++){P.shown.forEach(id=>__games.choose(id));__games.check();}} else {for(let i=0;i<5;i++) __games.choose(i===2?null:P.rounds[i].opts[i%4]);}
 const c=__games.cardData();__games.close();return ArxGameCard.result(c)}
