d3.json("/api/weather/chart/").then(d => chart(d));

const fieldTranslation = {
    'temperature': "Temperatura",
    'humidity': "Humidade",
    'rain': "P(Chuva)",
    'wind_strength': "Vento(km/h)",
};

function chart(data) {
    const keys = ["temperature", "humidity", "rain", "wind_strength"];
    const formatValue = d3.format(",.0f");
    const bisectDate = d3.bisector(d => d.hour).left;

    const svg = d3.select("#chart"),
        margin = {top: 15, right: 10, bottom: 5, left: 25},
        width = +svg.attr("width"),
        height = +svg.attr("height") - margin.top - margin.bottom;

    const x = d3.scaleTime()
        .rangeRound([margin.left, width - margin.right])
        .domain(d3.extent(data, d => d.hour));

    const y = d3.scaleLinear().rangeRound([height - margin.bottom, margin.top]);
    const z = d3.scaleOrdinal(["#990011", "#003dbf", "#003dbf", "#515967"]);

    const line = d3.line()
        .curve(d3.curveCardinal)
        .x(d => x(d.hour))
        .y(d => y(d.val));

    svg.append("g")
        .attr("class", "x-axis")
        .attr("transform", "translate(0," + (height - margin.bottom) + ")")
        .call(d3.axisBottom(x).tickFormat(d3.format("d")));

    svg.append("g")
        .attr("class", "y-axis")
        .attr("transform", "translate(" + margin.left + ",0)");

    const focus = svg.append("g")
        .attr("class", "focus")
        .style("display", "none");


    // Overlay
    svg.append("rect")
        .attr("class", "overlay")
        .attr("x", margin.left)
        .attr("width", width - margin.right - margin.left)
        .attr("height", height);

    update();

    function update() {
        const copy = keys;
        const metrics = copy.map((id) => {
            return {
                id: id,
                values: data.map(d => {
                    return {hour: d.hour, val: +d[id]}
                })
            };
        });

        y.domain([
            d3.min(metrics[0].values, d => d.val - 1),
            d3.max(metrics[0].values, d => d.val + 1)
        ]).nice();

        svg.selectAll(".y-axis")
            .transition()
            .call(d3.axisLeft(y).tickSize(-width + margin.right + margin.left));

        let metric = svg.selectAll(".cities").data([metrics[0]]);

        metric.enter().insert("g", ".focus").append("path")
            .attr("class", "line").style("stroke", d => z(d.id)).merge(metric)
            .transition().attr("d", d => line(d.values));
        tooltip(copy);
    }

    function tooltip(copy) {
        const labels = focus.selectAll(".lineHoverText").data(copy);

        labels.enter().append("text")
            .attr("class", "lineHoverText")
            .style("fill", d => z(d))
            .attr("text-anchor", "start")
            .attr("font-size", 12)
            .attr("dy", (_, i) => 1 + i * 2 + "em")
            .merge(labels);

        const circles = focus.selectAll(".hoverCircle").data(copy);

        circles.enter().append("circle")
            .attr("class", "hoverCircle")
            .style("fill", d => z(d))
            .attr("r", 2.5)
            .merge(circles);

        svg.selectAll(".overlay")
            .on("mouseover", () => {
                focus.style("display", null);
            })
            .on("mouseout", () => {
                focus.style("display", "none");
            })
            .on("mousemove", (e) => {
                const x0 = x.invert(d3.pointer(e)[0]),
                    i = bisectDate(data, x0, 1),
                    d0 = data[i - 1],
                    d1 = data[i],
                    d = x0 - d0.hour > d1.hour - x0 ? d1 : d0;

                focus.select(".lineHover")
                    .attr("transform", "translate(" + x(d.hour) + "," + height + ")");

                focus.select(".lineHoverDate")
                    .attr("transform", "translate(" + x(d.hour) + "," + (height + margin.bottom) + ")")
                    .text(d.hour);

                focus.selectAll(".hoverCircle")
                    .attr("cy", e => y(d[e]))
                    .attr("cx", x(d.hour));

                focus.selectAll(".lineHoverText")
                    .attr("transform",
                        "translate(" + (x(d.hour)) + "," + height / 2.5 + ")")
                    .text(e => e === 'temperature' ?
                        fieldTranslation[e] + " " + formatValue(d[e]) + "º" :
                        fieldTranslation[e] + ":" + formatValue(d[e]));

                x(d.hour) > (width - width / 4)
                    ? focus.selectAll("text.lineHoverText")
                        .attr("text-anchor", "end")
                        .attr("dx", -10)
                    : focus.selectAll("text.lineHoverText")
                        .attr("text-anchor", "start")
                        .attr("dx", 10)
            });
    }
}