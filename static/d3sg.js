function chart(chart_location, width, height) {


	if (width == undefined) {
		width = 800
	}
	if (height == undefined) {
		height = 400
	}

	$(chart_location).empty();

	this.MARGIN = {top: 80, right: 50, bottom: 50, left: 70};
	this.WIDTH = width - this.MARGIN.left - this.MARGIN.right;
	this.HEIGHT = height - this.MARGIN.top - this.MARGIN.bottom;
	x_scale = d3.time.scale().range([0, this.WIDTH]);
	y_scale = d3.scale.linear().range([this.HEIGHT, 0]);
	parseDate = d3.time.format("%Y-%m-%d").parse;
	this.DATA = []
	this.DATA_DICT = {}
	this.LINE_DICT = {}
	this.chart_location = chart_location
	this.LINE_NUM = 0
	this.LABEL_DICT = {}


	this._LOLLIPOP = [  {"color":"#5DA5DA","alpha":1,'linestyle':'-'},
              {"color":"#FAA43A","alpha":1,'linestyle':'-'},
              {"color":"#60BD68","alpha":1,'linestyle':'-'},
              {"color":"#F17CB0","alpha":1,'linestyle':'-'},
              {"color":"#B2912F","alpha":1,'linestyle':'-'},
              {"color":"#B276B2","alpha":1,'linestyle':'-'},
              {"color":"#DECF3F","alpha":1,'linestyle':'-'},
              {"color":"#F15854","alpha":1,'linestyle':'-'},
              {"color":"#4D4D4D","alpha":1,'linestyle':'-'},]


	this._create_canvas = function() {

		this.svg = d3.select(this.chart_location)
			.append("svg")
			.attr("width", this.WIDTH + this.MARGIN.left + this.MARGIN.right)
			.attr("height", this.HEIGHT + this.MARGIN.top + this.MARGIN.bottom)

		this.svg.append("rect")
		    .attr("width", "100%")
		    .attr("height", "100%")
		    .attr("fill", "#f5f5f5");

		this.g = this.svg.append("g")
			.attr("transform", "translate(" + this.MARGIN.left + "," + this.MARGIN.top + ")");
	}


	this._create_data_for_d3 = function (x, y, label) {

		// Put in correct format
		this.DATA = []
			for (var i = 0; i < x.length; i += 1) {
				var current_dict = {};
				current_dict['y'] = y[i];
				// current_dict['y2'] = y2[i];
				current_dict['x'] = x[i];
			    this.DATA.push(current_dict);
			}

		// Make sure X is dates, Y is numeric
		this.DATA.forEach(function(d) {
			d.x = parseDate(d.x);
			d.y = +d.y;
		});

		this.DATA_DICT[label] = this.DATA

	}


	this._scale_data = function(label) {

		var data_dict = this.DATA_DICT

		// Get global max
		var curr_max = 0;
		var curr_min = 0;
		$.each(data_dict, function( index, value ) {
		 	var new_max = d3.max(data_dict[index], function(d) { return d.y; })
		 	var new_min = d3.min(data_dict[index], function(d) { return d.y; })

		 	if (new_max >= curr_max) {
		  		curr_max = new_max;
		 	}
		 	if (new_min < curr_min) {
		  		curr_min = new_min;
		 	}
		});

		var current_data = this.DATA_DICT[label]
		x_scale.domain(d3.extent(current_data, function(d) { return d.x; }));
		y_scale.domain([curr_min, curr_max]);
	}


	this._draw_line = function(label) {

		this.g.selectAll("path").remove();

		var current_g = this.g;
		var color_scheme = this._LOLLIPOP;
		var line_num = 0;
		var data_dict = this.DATA_DICT
		var line_dict= this.LINE_DICT

		var index = label
		// console.log(data_dict[index])

		$.each(data_dict, function( index, value ) {

			// Have colors loop
			line_num = line_num % 9;

			var valueline = d3.svg.line()
				.x( function(d) { return x_scale(d.x); })
				.y( function(d) { return y_scale(d.y); });

			line_dict[index] = valueline

			// console.log(valueline)

			current_g.append("path")
				.attr("d", valueline(data_dict[index]))
				.style("stroke",color_scheme[line_num]["color"])
				.attr("id",index)
				.attr("class","line");

			line_num = line_num + 1

		});
		
	}
	


	this._add_axes = function() {

		this.svg.selectAll("g.axis").remove();

		xAxis = d3.svg.axis().scale(x_scale)
			.orient("bottom").ticks(5);
		yAxis = d3.svg.axis().scale(y_scale)
			.orient("left").ticks(5);

		this.g.append("g") // Add the X Axis
			.attr("class", "x axis")
			.attr("transform", "translate(0," + this.HEIGHT + ")")
			.call(xAxis);
		this.g.append("g") // Add the Y Axis
			.attr("class", "y axis")
			.call(yAxis);
	}


	this.line = function(x, y, label) {

		var underscore_label = 'series_' + this.LINE_NUM;
		if (label == undefined) {label = underscore_label};
		this.LABEL_DICT[label] = underscore_label;

		this._create_data_for_d3(x, y, underscore_label);
		this._scale_data(underscore_label);
		this._add_grid_lines();
		this._draw_line(underscore_label);
		this._add_axes();
		this._add_legend(label);
		this.LINE_NUM = this.LINE_NUM + 1;

	}



	this._add_default_title = function() {
		var title = "ch.set_title('My Title')"
		this.g.append("text")
			.attr("id","title")
			.attr("x", 0)
			.attr("y", 0 - (this.MARGIN.top / 2))
			.attr("font-family","sans-serif")
			.style("font-size", "18px")
			.style("font-weight", "bold")
			.text(title);
	}
	this.set_title = function(title) {
		title_obj = this.g.select("#title");
		title_obj.html(title);
	}


	this._add_default_subtitle = function() {
		var subtitle = "ch.set_subtitle('This is my default subtitle')"
		this.g.append("text")
			.attr("id","subtitle")
			.attr("x", 0)
			.attr("y", 0 - (this.MARGIN.top / 4))
			.attr("font-family","sans-serif")
			.style("font-size", "14px")
			.text(subtitle);
	}
	this.set_subtitle = function(subtitle) {
		title_obj = this.g.select("#subtitle");
		title_obj.html(subtitle);
	}


	this._add_grid_lines = function(subtitle) {

		this.svg.selectAll("g.grid").remove();

		function make_x_axis() {
			return d3.svg.axis()
			.scale(this.x_scale)
			.orient("bottom")
			.ticks(6)
		}
		function make_y_axis() {
			return d3.svg.axis()
			.scale(this.y_scale)
			.orient("left")
			.ticks(5)
		}

		this.g.append("g")
			.attr("class", "grid")
			.attr("transform", "translate(0," + this.HEIGHT + ")")
			.call(make_x_axis()
			.tickSize(-this.HEIGHT, 0, 0)
			.tickFormat("")
		)
		this.g.append("g")
			.attr("class", "grid")
			.call(make_y_axis()
			.tickSize(-this.WIDTH, 0, 0)
			.tickFormat("")
		)
	}


	this._add_default_ylabel = function() {
		this.svg.append("text")
			.attr("transform", "rotate(-90)")
			.attr("y", 0 + this.MARGIN.left/4) // minus goes left
			.attr("x", 0 - ((this.MARGIN.top + this.MARGIN.bottom + this.HEIGHT)/2)) // minus goes down 
			.attr("dy", "1em")
			.style("text-anchor", "middle")
			.attr("id","ylabel")
			.text("ch.set_ylabel('My Label')");
	}
	this.set_ylabel = function(ylabel) {
		label_obj = this.svg.select("#ylabel");
		label_obj.html(ylabel);
	}



	this.update_line = function(x, y, label) {

			// var underscore_label = 'series_' + this.LINE_NUM;
			// if (label == undefined) {label = underscore_label};


			underscore_label = this.LABEL_DICT[label];

			line_dict = this.LINE_DICT
			valueline = line_dict[underscore_label]
			this._create_data_for_d3(x, y, underscore_label);
			this._scale_data(underscore_label);
			data = this.DATA_DICT[underscore_label]
			// Select the section we want to apply our changes to
			var svg = d3.select(this.chart_location).transition();
			// Make the changes



			svg.select('#'+underscore_label)
				.duration(750)
				.attr("d", valueline(data));
			svg.select(".x.axis") // change the x axis
				.duration(750)
				.call(xAxis);
			svg.select(".y.axis") // change the y axis
				.duration(750)
				.call(yAxis);

	}


	this._add_legend = function(label) {

		this.svg.append("text")
			.attr("y", this.LINE_NUM*15 + this.MARGIN.top) // adding goes down
			.attr("x", 30 + 1.5*this.MARGIN.left) // minus goes down 
			.attr("dy", "0.3em")
			.style("text-anchor", "left")
			.attr("id","ylabel")
			.text(label);

		this.svg.append("line")
			.attr("x1", 0 + 1.5*this.MARGIN.left) // minus goes down 
			.attr("x2", 25 + 1.5*this.MARGIN.left) // minus goes down 
			.attr("y1", this.LINE_NUM*15 + this.MARGIN.top) // adding goes down
			.attr("y2", this.LINE_NUM*15 + this.MARGIN.top)
			.attr("stroke-width", 2)
            .attr("stroke", this._LOLLIPOP[this.LINE_NUM]["color"]); // adding goes down


	}



	
	this._create_canvas();
	this._add_default_title();
	this._add_default_subtitle();
	this._add_default_ylabel();
	this._add_legend();




	// // X axis label
	// this.svg.append("text")
	// 	.attr("y", (this.MARGIN.top + this.MARGIN.bottom + this.HEIGHT) / 2)
	// 	.attr("x", (this.MARGIN.left + this.MARGIN.right + this.WIDTH) / 2)
	// 	.attr("dy", "1em")
	// 	.style("text-anchor", "middle")
	// 	.text("Date");



};
