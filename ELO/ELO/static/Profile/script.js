$(document).ready(function(){

    $dialog = $(".dialog").dialog({
        autoOpen: false,
        hide: "slideUp",
        modal: true,
        resizable: false,
    });

    $("button[id^='edit_']").click(function(){
        field = $(this).attr("id").slice(5);
        fname = $(this).attr("title")

        // Gets the title of the dialog from the title of button.
        $dialog.dialog("option", "title", fname);

        $dialog.load("/assync/editfield/"+field, function(){
            $dialog.dialog("open");
        });
    });

    var $pc = $('#progressController');
    var $pCaption = $('.progress-bar p');
    var iProgress = document.getElementById('inactiveProgress');
    var aProgress = document.getElementById('activeProgress');
    var iProgressCTX = iProgress.getContext('2d');
    var courseName = document.getElementById("courseName").value;

    var percentage = $pc.val() / 100;
    drawProgress(aProgress, percentage, $pCaption);
    
    drawInactive(iProgressCTX);

    function drawInactive(iProgressCTX){
        iProgressCTX.lineCap = 'square';

        //outer ring
        iProgressCTX.beginPath();
        iProgressCTX.lineWidth = 15;
        iProgressCTX.strokeStyle = '#e1e1e1';
        iProgressCTX.arc(137.5,137.5,129,0,2*Math.PI);
        iProgressCTX.stroke();

        //progress bar
        iProgressCTX.beginPath();
        iProgressCTX.lineWidth = 0;
        iProgressCTX.fillStyle = '#e6e6e6';
        iProgressCTX.arc(137.5,137.5,121,0,2*Math.PI);
        iProgressCTX.fill();

        //progressbar caption
        iProgressCTX.beginPath();
        iProgressCTX.lineWidth = 0;
        iProgressCTX.fillStyle = '#fff';
        iProgressCTX.arc(137.5,137.5,100,0,2*Math.PI);
        iProgressCTX.fill();

    }
    
    function drawProgress(bar, percentage, $pCaption){
        var barCTX = bar.getContext("2d");
        var quarterTurn = Math.PI / 2;
        var endingAngle = ((2*percentage) * Math.PI) - quarterTurn;
        var startingAngle = 0 - quarterTurn;

        bar.width = bar.width;
        barCTX.lineCap = 'square';

        barCTX.beginPath();
        barCTX.lineWidth = 20;
        barCTX.strokeStyle = '#76e1e5';
        barCTX.arc(137.5,137.5,111,startingAngle, endingAngle);
        barCTX.stroke();

        $pCaption.text( (parseInt(percentage * 100, 10)) + '%');
    }

});