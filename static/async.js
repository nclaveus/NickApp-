btn = document.getElementById('cam');
if(btn !=null){
    btn.onclick= function(){
        console.log("click");
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                console.log("enregistrement");
            }
        };
        firstn = document.getElementById("firstn").value;
        lastn = document.getElementById("lastn").value;
        token = Math.floor(100000 + Math.random() * 900000);
        if(firstn.length > 3 && lastn.length>3){
            xhttp.open("GET", "/saveimg?firstn="+firstn+"&lastn="+lastn+"&token="+token.toString(), true);
            xhttp.send(); 
        }else{
            alert("First name and last name must be filed before capturing avatar")
        }
    
        setTimeout(function(){
            avatar = document.getElementById("avatar")
            fname = firstn+"_"+lastn+"_"+token+"/"+"1.jpg"
            avatar.src = "/static/dataset/"+fname
    
            avatarimg = document.getElementById("avatarimg")
            avatarimg.value = "/static/dataset/"+fname
        }, 1000);
        
        
    
    }
    
}



btni = document.getElementById('cami');
if(btni !=null){
    btni.onclick= function(){
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                rep = xhttp.responseText
                if(rep=="0"){
                    console.log("face unrecognized")
                }else{
                    console.log(rep)
                    usen = document.getElementById('username');
                    usen.value=rep
                }
    
            }
        };
        //console.log("rec")
        xhttp.open("GET", "/facecheck", true);
        xhttp.send(); 
    
    }
    
    
}
