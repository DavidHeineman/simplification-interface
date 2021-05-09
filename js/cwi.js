// Chooses paragraph based on URL
function displayParagraph(data) {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    var pgNum = parseInt(urlParams.get('pg'));
    if (!Object.is(pgNum, NaN)) {
        $( '#paragraph-container' ).css('display', 'block');
        $( '#pg-num' ).html(pgNum);
        $( "#cwi-contents" ).html(data[pgNum].Text); //.replace(/\n/g, "<br />")
        enableCWI();
    } else {
        $( '#null-container' ).css('display', 'block');
    }
}
$.ajax({
    url: 'data.json',
    dataType: 'json',
}).done(displayParagraph);

// Allows clicking to change word color / difficulty
function enableCWI() {
    var words = $( "#cwi-contents" ).first().text().split( /\s+/ );
    var text = words.join( "</span> <span>" );
    $( "#cwi-contents" ).first().html( "<span>" + text + "</span>" );
    $( "span" ).on( "click", function() {
        if ($( this )[0].style.backgroundColor == "rgb(255, 157, 157)") {
            $( this ).css( "background-color", "rgb(255, 255, 255)" );
        } else if ($( this )[0].style.backgroundColor == "rgb(249, 255, 157)") {
            $( this ).css( "background-color", "rgb(255, 157, 157)" );
        } else {
            $( this ).css( "background-color", "rgb(249, 255, 157)");
        }
        
        var vartext = $(this)[0].innerText.replace(/[\W_]+/g,"").toLowerCase();
        var varcolor = $(this)[0].style.backgroundColor;
        $('#cwi-contents').children('span').each(function(content){
            if ($(this)[0].innerText.replace(/[\W_]+/g,"").toLowerCase() == vartext) {
                $( this )[0].style.backgroundColor = varcolor;
            }
        });
    });
}

// Compiles and downloads final output file
function submit() {
    var rows = []
    let csvContent = "data:text/csv;charset=utf-8,";
    $('#cwi-contents').children('span').each(function(content){
        var elem = []
        elem.push($(this)[0].innerText)
        if ($( this )[0].style.backgroundColor == "rgb(255, 157, 157)") {
            elem.push("2");
        } else if ($( this )[0].style.backgroundColor == "rgb(249, 255, 157)") {
            elem.push("1");
        } else {
            elem.push("0");
        }
        rows.push(elem)
    })
    rows.forEach(function(rowArray) {
        let row = rowArray.join("\t");
        csvContent += row + "\r\n";
    });
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    var pgNum = parseInt(urlParams.get('pg'));
    var encodedUri = encodeURI(csvContent);
    var link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "pg_" + parseInt(pgNum) + "_output.bin");
    document.body.appendChild(link);
    link.click();
}
$( "#submit" ).click(submit);

// Link next paragraph button to next paragraph
$( "#next-pg" ).click(function () {
    submit();
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    var pgNum = parseInt(urlParams.get('pg'));
    window.location.replace("cwi?pg=" + parseInt(pgNum + 1));
})