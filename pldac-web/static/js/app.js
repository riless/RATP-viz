$( function(){


    QUERY_URL = '/query/'
    window.query_map = 0; 
    window.query_distro = '0';
    window.query_routes = 0;
    window.query_paris = 1;
    window.query_filters = JSON.stringify(["1","2","3","3b","4","5","6","7","7b","8","9","10","11","12","13","14"]);
    window.query_date = '2015-05-16';
    window.flow_passagers = 0
    window.min_flow = 0;
    window.max_flow = 1;


    var slider = $("#flux-usagers-slider");


    $.getJSON('/flow_bounds').done(function(json){
        window.min_flow = json.flux_min;
        window.max_flow = json.flux_max;
        slider.noUiSlider({
            start: [json.flux_min, json.flux_max],
            range: {
                'min': json.flux_min,
                'max': json.flux_max
            },
            format: wNumb({
                decimals: 0
            }),
        });
        slider.Link('lower').to($('#min-flux'));
        slider.Link('upper').to($('#max-flux'));
    });

    $('#flux-usagers-cbx').click(function(){
        if ( $(this).is(':checked') ){
            slider.fadeIn("fast");
            window.flow_passagers = 1;
            window.min_flow = parseInt($('#min-flux').val()); 
            window.max_flow = parseInt($('#max-flux').val());
            update_map();   
        } else {
            slider.fadeOut("fast");parseInt
        }
    });

    slider.on('change', function(){
        window.min_flow = parseInt($('#min-flux').val()); 
        window.max_flow = parseInt($('#max-flux').val());
        update_map();
    });




    // $('#flux-usagers-slider').noUiSlider_pips({
    //     mode: 'values',
    //     values: [20, 80],
    //     density: 4
    // });
    

    function get_config(){
        return {
            'distro': window.query_distro,
            'routes': window.query_routes,
            'paris': window.query_paris,
            'filters': window.query_filters,
            'date': window.query_date,
            'flow_passagers': window.flow_passagers,
            'min_flow': window.min_flow,
            'max_flow': window.max_flow
        }
    }

    //declaration des variable de la requette
    var tiles = [ 
        {   'url': 'https://{s}.tiles.mapbox.com/v4/mapbox.dark/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoicmlsZXNzIiwiYSI6ImtYOXM4c00ifQ.NXbIrxVogudcrysJMNHjZg',
            'icon': '/static/map/mapbox.png',
            'title': 'Mapbox' },

        {   'url': 'http://{s}.tile.osm.org/{z}/{x}/{y}.png',
            'icon': '/static/map/osm.png',
            'title': 'Open Street Map' },

        {   'url': 'http://tile.stamen.com/watercolor/{z}/{x}/{y}.jpg',
            'icon': '/static/map/watercolor.png',
            'title': 'Stamen Watercolor' },
        ]


    // bend map to #map
    var map = L.map( 'map', {
        center: [48.8512, 2.3555],
        zoom: 13
    });
    
    setBase(tiles[window.query_map].url);

    var layers = new L.FeatureGroup();

    function drawJson(geojson, map){
            // layers.clearLayers();
            L.geoJson(geojson, {
                pointToLayer: function (feature, latlng) {
                    var marker_style = {
                        radius: feature.properties.radius,
                        fillColor: feature.properties.fill_color,
                        color: "#000",
                        weight: 1,
                        opacity: 0.4,
                        fillOpacity: 0.8,
                        clickable: true
                    };
                    return L.circleMarker(latlng, marker_style);
                },
                style: function(feature){
                    switch ( feature.geometry.type ){
                        case "Polygon": {
                            return {
                                radius: 4,
                                fillColor: "#000",
                                color: "#fff",
                                weight: 2,
                                opacity: 0.5,
                                fillOpacity: 0.5
                            };
                            break;
                        }
                        case "MultiLineString": {
                            return {
                                color: feature.properties.color,
                                weight: 1.5,
                                opacity: 0.2,
                            };
                            break;
                        }

                        case "LineString": {
                            if ( typeof feature.properties.value !== 'undefined'){
                                value = feature.properties.value
                            } else {
                                value = 1.5
                            }
                            return {
                                color: feature.properties.color,
                                weight: value,
                                opacity: 0.5,
                            };
                            break;
                        }
                    }
                },
                onEachFeature: function (feature, layer) {
                    switch ( feature.geometry.type ){
                        case "Point": {
                            var tooltip_content = '\
                            <div class="tt-head"><b>'+feature.properties.stop_name+'</b><br>\
                            <small>'+feature.properties.stop_cp+'</small></div> \
                            <div class="tt-corr">';
                            var transfers = feature.properties.stop_transfers.split(',')

                            for (i=0; i<transfers.length; i++){
                                tooltip_content += '<img src="static/img/indices/'+transfers[i].toLowerCase()+'.png"/>';
                            }

                            if ( feature.properties.data_value != 0 ){
                                avg_str = "<strong style='color:#c0392b'>"+feature.properties.rapport_avg+"</strong>"
                                avg_str_green = "<strong style='color:#28b061'>+"+feature.properties.rapport_avg+"</strong>"
                                if (feature.properties.rapport_avg >= 0){
                                    avg_str = avg_str_green
                                }
                                tooltip_content += '</div>\
                                <div class="tt-content">'
                                +'<h4>'+feature.properties.data_value.toFixed(1)+'</h4><br>'
                                +avg_str+' par rapport a la moyenne'
                                +'</div>\
                                ';
                            }

                            layer.bindPopup(tooltip_content);
                            break;
                        }
                    }

                }
            }).addTo(layers)// .bringToFront();
        layers.addTo(map);
    }


    function update_map(){
        map.removeLayer(layers);
        layers = new L.FeatureGroup();
        
        
        setBase(tiles[window.query_map].url);
        $.ajax({
            type: "POST",
            traditional: true,
            url: QUERY_URL,
            async: false,
            data: get_config(),
            dataType: "json",
            success: function(json) {
               drawJson(json.paris, map);
               // drawJson(json.flow, map);

               if (json.properties_distro.data_label == ""){
                    $("#map-title").text("Carte de paris")
                    $("#map-desc").text("Selectionnez une distribution dans le menu \"DISTROS\"")
               } else {
                    console.log(json.properties_distro.data_label)
                    $("#map-title").text(json.properties_distro.data_label)
                    $("#map-desc").text("Moyenne par station: ~"+json.properties_distro.avg_value.toFixed(1) )
               }

                $.each(json.flow, function(i, flux) {
                    var polyline = L.polyline(flux.chemin, {
                        color: flux.color,
                        weight: flux.value/2,
                        opacity: 0.8,
                        smoothFactor: 1
                    })

                    var decorator = L.polylineDecorator(polyline, 
                        { patterns: [
                            {offset: 50, repeat: 100, symbol: L.Symbol.arrowHead({pixelSize: flux.value * 2, pathOptions: {fillOpacity: 0.8, weight: 0, color: flux.color}})}
                        ] }
                    )
                    layers.addLayer(polyline)
                    layers.addLayer(decorator)
                    
                });
                layers.addTo(map);

                

               drawJson(json.routes, map);
               drawJson(json.distro, map);
            }
        });

    }

    function setBase(tile){
        L.tileLayer(tile, {
            attribution: 'Projet PLDAC'
        }).addTo(map);
    }

    function update_filters(){
        var filters = $("#route-list img:NOT(.element-disabled)").map(function(){return $(this).attr("route_id");}).get();
        
        window.query_filters = JSON.stringify(filters)

    }

/***************************************************
LISTENERS ON OPTIONS CHANGE 
****************************************************/

    // CHANGE DISTRO
    $('body').on('click', '#distro-list img', function(){

        $('#distro-list img').addClass('element-disabled');
        $(this).removeClass('element-disabled');

        window.query_distro = $(this).attr('distro_id');
        update_map();
    });

    // CHANGE MAP
    $('body').on('click', '#map-list img', function(){

        $('#map-list img').addClass('element-disabled');
        $(this).removeClass('element-disabled');

        window.query_map = $(this).attr('map_id');
        update_map();
    });

    // CHANGE FILTERS
    $('body').on('click', '.default-route', function(){
        if ( $(this).attr("route_id") == "select_nothing" ) {
            $("#route-list img:NOT(.default-route)").removeClass("element-disabled").addClass("element-disabled");
        } else {
            $("#route-list img:NOT(.default-route)").removeClass("element-disabled");
        }
        update_filters();
        update_map();
    });

    $('body').on('click', '#route-list img:NOT(.default-route)', function(){
        $(this).toggleClass('element-disabled');
        update_filters();
        update_map();
    });

    // PARIS 
    $('#check-paris').click(function(){
        if ( $(this).is(':checked') ) {
            window.query_paris = 1;
        } else {
            window.query_paris = 0;
        }
        update_map();
    });

    // delete distro
    $("body").on('click', '.distro-del a', function(){
        var distro_id = $(this).attr('del');

        $.getJSON('/del-disto/?del='+distro_id)
        .done( function(json){
            if ( json['stat'] == 'success' ){
                $("a[del='"+distro_id+"']").parent().parent().fadeOut();
            }
        });
    });
    $("#upload-data-form").on("submit", function (e) {
        e.preventDefault();
        var formData = new FormData(this);
        formData.append( 'data_icon', $("#data-icon")[0].files );
        formData.append( 'data_file', $("#data-file")[0].files );
        var action = $(this).attr("action")
        $.ajax({
            url: action,
            type: "POST",
            data: formData,
            processData: false,  // tell jQuery not to process the data
            contentType: false   // tell jQuery not to set contentType
        });
        $("#file-loaded").slideUp();
        $(this)[0].reset();
        $("#data_mod").click();
        return false;
    })


function animate_train(){
    /* ANIMATE TRAINS */
    var myIcon = L.icon({
        iconUrl: 'static/img/pin.svg',
        iconSize:  [32, 32],
        iconAnchor: [16, 32],
        shadowUrl: null
    });

    var d = new Date(2015,04,16, 5,30,00);
    time_data = {
        "year": d.getFullYear(),
        "month": d.getMonth(),
        "day": d.getDate(),
        "hour": d.getHours(),
        "minute": d.getMinutes(),
        "second": d.getSeconds(),
    }

    $.post('/trains', time_data, function(json_str){
        json = $.parseJSON(json_str)

        $.each(json, function(i, routeLine) {
            var line = L.polyline(routeLine)
            var animatedMarker = L.animatedMarker(line.getLatLngs(), {
                interval: 500, // milliseconds
                icon: myIcon,
                onEnd: function() {
                    $(this._shadow).fadeOut();
                    $(this._icon).fadeOut(2000, function(){
                        map.removeLayer(this);
                    });
                }
            });
            map.addLayer(animatedMarker);
            animatedMarker.start();
        });
    });
}

/***************************************************
CONTROLS
****************************************************/

	var side_panel = "#side-panel";
	var side_buttons = "#side-buttons a";

	function collapse_sidebar(){
		$( side_buttons ).removeClass("selected");
		$( side_panel ).animate({"right": "-400px"}, 200);
	}

	function expend_sidebar(){
		$(side_panel).animate({"right": "0"}, 200);
	}


    // $('select#calendar-list').on('change', function() {
    //     window.query_date = this.value;
    // });

    $.getJSON('/calendars').done(function(json){
        for (i=0; i < json.length; i++){
            attributes =  {
                "value": json[i]['value'],
                "text": json[i]['text']
            };

            if ( json[i]['selected'] == '1' ){
                attributes['selected'] = "selected";
            }


            $('#calendar-list').append(
                $('<option>', attributes )
            );
        }
    });



    map_list = $("#map-list");
    map_list.empty();

    for (i=0; i < tiles.length; i++){
        class_disabled = ""
        if ( i != 0 )
            class_disabled = "element-disabled"

        map_list.append( $( "<img>")
            .attr('src', tiles[i].icon )
            .attr('map_id', i )
            .attr('titre', tiles[i].title )
            .attr('class', class_disabled)
        )
    }

    $.getJSON('/route-list').done(function(json){
        $("#route-list img:NOT(.default-route)").remove();
        for (i=0; i < json.length; i++){
            $("#route-list").append( $('<img>')
                .attr('src', 'static/img/indices/' + json[i]['route_short_name'] + '.png')
                .attr('route_id', json[i]['route_short_name'])
            )
        }
    });

    $("#start-visu").click(function(){
        window.query_date = $("select#calendar-list").val();
        update_map();
        $("#welcome").fadeOut();
        $("#map-info").fadeIn();
    })



	$(side_buttons).click(function(){
		// 
		$(side_buttons).not(this).removeClass("selected");
		$(this).toggleClass("selected");
		if ( !$(side_buttons).hasClass("selected") ){
			collapse_sidebar();
		} else {
			expend_sidebar();
			// views
			var editor = "#" + $(this).attr("id")+"_editor";
			$(".editor").hide();
			$( editor ).show();

            if ( editor == '#data_mod_editor'){
                var table = $("#distro-table").find('tbody');
                table.empty();
                $.getJSON('/distro-list').done(function(json){
                    for (i=0; i < json.length; i++){
                        tr = table.append( $('<tr>') 
                            .append($('<td class="distro-icon">').append(
                                $('<img>').attr('src', 'static/icons/'+json[i]["data_icon"])
                            ))

                            .append($('<td class="distro-label">').text(
                                json[i]["data_label"]
                            ))

                            .append($('<td class="distro-del">').append(
                                $('<a href="#">').attr('del', json[i]["data_id"])
                            ))
                        );
                    }
                });
            }

            // LIGNES
            // DISTROS
            // $("#distro-list").on('click', 'img', function(){
            //     $(this).toggleClass('element-disabled');
            // })
            if ( editor == '#distro_mod_editor'){
                $.getJSON('/distro-list').done(function(json){
                    $("#distro-list img:NOT(.default-distro)").remove();
                    for (i=0; i < json.length; i++){
                        $("#distro-list").append( $('<img>')
                            .attr('src', 'static/icons/' + json[i]['data_icon'])
                            .attr('distro_id', json[i]['data_id'] )
                            .attr('class', 'element-disabled' )
                            .attr('title', json[i]['data_label'] )
                        )
                    }
                    $("img[distro_id="+window.query_distro+"]").removeClass("element-disabled");
                });
            }
		}
	});

    
	// when clicked outside of side-panel
	$(document).mouseup(function (e) {
	    if (!$(side_panel).is(e.target) && $(side_panel).has(e.target).length === 0) {
	        collapse_sidebar();
	    }
	});



	/***************************************************
	FILTERS
	****************************************************/

	$('.filter-ligne').click(function(){
		$.getJSON("/routes").done(function(json){
			map.clearLayers();
        	map.addData( json  );
        });
	});        


    /***************************************************
    UPLOAD
    ****************************************************/

    $(document).ready(function(){
        $('#data-file').on('change', function(e){
            if ( $(this).val() != '' ){
                readFile(this.files[0], function(e) {
                    var csv = Papa.parse( e.target.result ).data
                    $('#upload-cp, #upload-values').find('option:not(.default-select)').remove();
                    for (i = 0; i < csv[1].length; i++){
                        $('#upload-cp, #upload-values').append($('<option>', {
                            value: i,
                            text: "Colonne "+i+" ("+csv[1][i]+")",
                            exemple: csv[1][i]
                        }));
                    }
                    $('#file-loaded').slideDown();
                });
            } else {
                $('#file-loaded').slideDown();
            }
        });
    });

    function readFile(file, onLoadCallback){
        var reader = new FileReader();
        reader.onload = onLoadCallback;
        reader.readAsText(file);
    }

    /* vérifier code postal */
    $("#upload-cp").on("change", function(e){
        regex = /([0-9]{1,2})(?!.*\d)(eme|e\.|ere|er|e)?[\w ]*?$/
        var v = $('option:selected', this).attr('exemple');
        // match = regex.exec(v)
        // console.log( match[0] )
        if ( !regex.test(v) ){
            $(this).addClass('wrong-select')
        } else {
            $(this).removeClass('wrong-select')
        }
    });


    /*check image dimensions*/
    var reader = new FileReader();
    var image  = new Image();

    $("#data-icon").on("change", function(e){
        if ( $(this).val() != '' && this.files[0] ){
            file = this.files[0];
            var reader = new FileReader();
            var image  = new Image();

            reader.readAsDataURL(file);  
            reader.onload = function(_file) {
                image.src    = _file.target.result;
                image.onload = function() {
                    if (this.width == 32 && this.height == 32 ){
                        $("#icon-preview").html('<img src="'+this.src+'">');
                    } else {
                        $("#icon-preview").html('');
                    }
                };
                image.onerror= function() {
                    $("#icon-preview").html('');
                };      
            };
        } else {
            $("#icon-preview").html('');
        }
    });



});