var pk_list=[]
$('.search-label').on('click', function(event) {
    $('.error-list').empty();

    if (validateSearchForm()) {
        $.ajax({
            url: '/studentnest/search-property?' + $('.search-form').serialize(),
            type: 'GET',
            data: $(this).serialize(),
            success: updateChanges
        });
    }
});
function drawWordCloud2(id,aptnamelist) {
            if(aptnamelist=='undefined' || aptnamelist==null)
                var frequency_list = []
            else
                var frequency_list = aptnamelist;

            var fill = d3.scale.category20();

            var word_Cloud_id = '#cloud' + id;
            var color = d3.scale.linear()
                    .domain([0, 1, 2, 3, 4, 5, 6, 10, 15, 20, 100])
                    .range(["#e5e5ff", "#b2b2ff","#ff6666", "#99cc99","#7f7fff", "#3232ff","#ff1919", "#4ca64c","#000e5", "#000099", "#000066", "#000033", "#000000"]);

            d3.layout.cloud().size([280, 280])
                    .words(frequency_list, id)
                    .rotate(0)
                    .fontSize(function (d) {
                        return d.size * 15;
                    })
                    .on("end", draw)
                    .start();


            function draw(words) {
                d3.select(word_Cloud_id).select("svg").remove();
                d3.select(word_Cloud_id).append("svg")
                        .attr("width", 300)
                        .attr("height", 280)
                        .attr("class", "wordcloud")
                        .append("g")
                        // without the transform, words words would get cutoff to the left and top, they would
                        // appear outside of the SVG area
                        .attr("transform", "translate(82,150)")
                        .selectAll("text")
                        .data(words)
                        .enter().append("text")
                        .style("font-size", function (d) {
                            return d.size + "px";
                        })
                        .style("fill", function(d, i) { return fill(i); })
                        .attr("transform", function (d) {
                            return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
                        })
                        .text(function (d) {
                            return d.text;
                        });
            }
        }


function updateChanges(data) {
    //clean old data
    $(".property-list").html("");
    pk_list = [];
    var property_list=$('.property-list');
    for (var i = 0; i < data.properties.length; i++) {
              var property = data.properties[i];
              pk_list.push(property.pk);
              var review = property.highest_vote_review;
              property_list.append( '<div id="'+property.pk+'" ><div class="row">'+
                                        '<div class="property-wrapper">'+
                                            '<div class="col s12 m7">'+
                                                '<div class="card">'+
                                            '<div class="card-image waves-effect waves-block waves-light">'+
                        '<a href="details/'+property.pk+'" ><img src="'+property.image_url+'"></a>'+
                    '</div>'+
                    '<div class="card-content">'+
                        '<div class="row">'+
                            '<div class="col s11 m9">'+
                                '<a href="details/'+property.pk+'"><span class="card-title grey-text text-darken-4">'+property.name+'</span></a>'+
                                    '<p>'+property.street+', '+property.city+', '+property.state+' '+property.zip+'</p>'+
                                '<div id="property-rating-'+property.pk+'"></div>'+
                            '</div>'+
                            '<div class="col s11 m2">'+
                                '<span class="card-title blue-text property-price-text">'+ '$' + property.price+'</span>'+
                                '<div class="bedroom-num-wrapper">'+
                                    '<div class="bedroom-num-text">'+property.min_bedroom_num+'~'+property.max_bedroom_num+' </div>'+
                                    '<div class="bedroom-icon-wrapper">'+
                                        '<img src="/static/studentnest/images/bedroom_icon.ico" class="bedroom-icon">'+
                                    '</div>'+
                                '</div>'+
                            '</div>'+
                        '</div></div></div></div>'+
            '<div class="col s12 m5">'+
                '<div class="word-cloud-wrapper">'+
                     '<div class="card">'+
                        '<div id="cloud'+property.pk+'">'+
                        '</div></div></div>'+
                '<div class="review-wrapper">'+
                    '<div class="card grey darken-1">'+
                        '<div class="card-content white-text">'+
                            '<div class="row">'+
                                '<div class="col s12 m8">'+
                                    '<p class="review-title">Review</p>'+
                                '</div>'+
                                '<div class="col s12 m4">'+
                                    '<div class="like-num-wrapper">'+
                                    '<div class="like-num-text">'+property.highest_vote_review.votes+'</div>'+
                                    '<div class="like-icon-wrapper">'+
                                        '<img src="/static/studentnest/images/like-flat.png" class="like-icon">'+
                                    '</div></div></div></div>'+
                            '<p>'+property.highest_vote_review.content+'</p>'+
                        '</div></div></div></div></div></div>'+
      '<div class="divider property-list-divider"></div></div>'
              );
        $("#property-rating-"+property.pk).ready(function () {
            $("#property-rating-"+property.pk).rateYo({
                    rating: property.rating,
                    readOnly: true,});
        });
        drawWordCloud2(property.pk, property.keywords);
    }
}


// property.highest_vote_review.votes+

function validateSearchForm() {
    var errors = [];

    if($('[name="location"]').val() == "") {
        errors.push("Location field cannot be empty.");
    }

    if (parseInt($('[name="min_bedroom_num"]').val()) != "0" && parseInt($('[name="max_bedroom_num"]').val()) != "65535"
        && parseInt($('[name="min_bedroom_num"]').val()) > parseInt($('[name="max_bedroom_num"]').val())) {
        errors.push("Min bedroom number cannot be greater than max bedroom number.");
    }

    if (parseInt($('[name="min_price"]').val()) != "-1" && parseInt($('[name="max_price"]').val()) != "102400"
        && parseInt($('[name="min_price"]').val()) > parseInt($('[name="max_price"]').val())) {
        errors.push("Min price cannot be greater than max price.");
    }

    for (var i = 0; i < errors.length; i++) {
        $('.error-list').append('<li>' + errors[i] + '</li>');
    }

    if (errors.length == 0) {
        return true;
    } else return false;
}

$(document).ready(function() {
    $('select').material_select();
});