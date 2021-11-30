from browser import window

"""Q&D module to do ajax requests with data types currently unsupported by Brython"""
# FIXME: remove this module when official aio module allows to work with blobs

window.eval("""
var _tmp_ajax = function(method, url, format, data){
    return new Promise(function(resolve, reject){
        var xhr = new XMLHttpRequest()
        xhr.open(method, url, true)
        xhr.responseType = format
        xhr.onreadystatechange = function(){
            if(this.readyState == 4){
                resolve(this)
            }
        }
        if(data){
            xhr.send(data)
        }else{
            xhr.send()
        }
    })
}
""")

ajax = window._tmp_ajax
