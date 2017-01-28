var container = document.getElementById('item-gallery');
function Searcher() {
    this.get_args();
    this.show_query();
    this.build_index();
    this.search();
}
Searcher.prototype = {
    query: '',

    get_args: function() {
        var bits = window.location.search.slice(1).split('&');
        var out = {};
        bits.forEach(function(b) {
            var bit = b.split('=');
            var name = decodeURIComponent(bit[0]);
            var value = decodeURIComponent(bit[1]).replace('+',' ');
            out[name] = value;
        });
        this.args = out;
        this.query = this.args['q'] || '';
        return out;
    },

    show_query: function() {
        var s = this;
        Array.prototype.forEach.apply(container.querySelectorAll('.query'),[function(q) { 
            q.textContent = s.query; 
        }]);
    },

    build_index: function() {
        var s = this;
        if(this.index) {
            return;
        }
        this.index = lunr(function() {
            this.field('title',{boost:10});
            this.field('author');
            this.field('description');
            this.field('keywords');
            this.field('references');
            this.field('requirements');
            this.ref('filename');
        });
        this.content_dict = {};
        var items = JSON.parse(document.getElementById('notebook-data').textContent);
        console.log(items);
        items.forEach(function(d) {
            s.content_dict[d.url] = d;
            s.index.add(d);
        });
        console.log(s.index);
    },

    search: function(query) {
        if(query!==undefined) {
            this.query = query.trim();
        }
        window.history.replaceState({},'',window.location.pathname+(this.query ? '?q='+encodeURIComponent(this.query) : ''));
        var s = this;

        if(!this.query) {
            container.classList.remove('searching');
            return;
        }
        container.classList.add('searching');

        var results = this.index.search(this.query);

        if(results.length) {
            container.classList.add('got-results');
        } else {
            container.classList.remove('got-results');
        }

        var item_map = {}

        for(let card of document.querySelectorAll('.item')) {
            var filename = card.getAttribute('data-filename');
            item_map[filename] = card;
            card.classList.remove('search-hit');
        }
        results.forEach(function(r) {
            item_map[r.ref].classList.add('search-hit');
        });

        localStorage['search-query'] = this.query;
    }
}

var searcher = new Searcher();


var query_input = document.getElementById('search-query')
query_input.addEventListener('input',function() {
    searcher.search(query_input.value);
});
query_input.value = searcher.query || '';
