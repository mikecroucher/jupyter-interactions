function match(query,string) {
    if(string.slice(0,query.length).toLowerCase() == query.toLowerCase()) {
        return true;
    }
}
function search() {
    query = query_input.value.trim();
    if(!query) {
        document.getElementById('item-gallery').classList.remove('searching');
        return;
    }
    document.getElementById('item-gallery').classList.add('searching');

    var items = document.querySelectorAll('#item-gallery .item');
    Array.prototype.forEach.apply(items,[function(item) {
        var keywords = item.getAttribute('data-keywords').split(',');
        if(keywords.some(function(word){return match(query,word)})) {
            item.classList.add('search-hit');
            console.log(item);
        } else {
            item.classList.remove('search-hit');
        }
    }]);
}

var query_input = document.getElementById('search-query')
query_input.addEventListener('input',search);
search();
