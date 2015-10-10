$(document).ready(function(){

	$("#acc_search").submit(function(e){
		e.preventDefault();

		var result = {};
		var postData = $(this).serializeArray();

		$.each( postData, function( i, pD ) {
  			result[pD.name] = pD.value;
      	});
	
      	model = $("h2[id^='mod_']").attr("id").slice(4);
      	result["model"] = model;
      	result['act'] = "search";

		$(".container").load("adm/"+model+"/search/", result);
	});

	$("#new_acc").click(function(){
		model = $("h2[id^='mod_']").attr("id").slice(4);
		$(".container").load("adm/new"+model+"/");
	});

	$("#del_acc").click(function(){
		model = $("h2[id^='mod_']").attr("id").slice(4);
		$(".container").load("adm/del"+model+"/");
	});

	$("#reg_form").submit(function(e){
		e.preventDefault();

		var result = {};
		var postData = $(this).serializeArray();

		$("#dialog-confirm").html("Deseja confirmar esta ação?");

		model = $("h2[id^='mod_']").attr("id").slice(4);

		$("#dialog-confirm").dialog({
	        resizable: false,
	        modal: true,
	        title: "Confimação",
	        height: 150,
	        width: 250,
	        buttons: {
	            "Yes": function () {
	            	$.each( postData, function( i, pD ) {
			  			result[pD.name] = pD.value;
			      	});
			      	
			      	result["model"] = model;
			      	result["act"] = "reg";

			      	$(this).dialog('close');

					$(".container").load("adm/"+model+"/register/",result);
	            },
	            "No": function () {
	                $(this).dialog('close');
	                model = "src"+model;

	                $(".container").load("/adm/"+model);
	            }
	        }
	    });
		
	});

	$("#del_form").submit(function(e){
		e.preventDefault();

		var result = {};
		var postData = $(this).serializeArray();

		$.each( postData, function( i, pD ) {
  			result[pD.name] = pD.value;
      	});

      	model = $("h2[id^='mod_']").attr("id").slice(4);

      	result["model"] = model;

		$("#dialog-confirm").html("Deseja confirmar esta ação?");
		
		$("#dialog-confirm").dialog({
	        resizable: false,
	        modal: true,
	        title: "Confimação",
	        height: 150,
	        width: 250,
	        buttons: {
	            "Yes": function () {
	            	$.each( postData, function( i, pD ) {
			  			result[pD.name] = pD.value;
			      	});
			      	
			      	result["model"] = model;
			      	result["act"] = "del";

			      	$(this).dialog('close');

					$(".container").load("adm/"+model+"/delete/",result);
	            },
	            "No": function () {
	                $(this).dialog('close');
	                model = "src"+model;

	                $(".container").load("/adm/"+model);
	            }
	        }
	    });
    }); 
  	
	$("#edit_form").submit(function(e){
		e.preventDefault();

		var result = {};
		var postData = $(this).serializeArray();

		$("#dialog-confirm").html("Deseja confirmar esta ação?");

      	model = $("h2[id^='mod_']").attr("id").slice(4);

		$("#dialog-confirm").dialog({
	        resizable: false,
	        modal: true,
	        title: "Confirmação",
	        height: 150,
	        width: 250,
	        buttons: {
	            "Yes": function () {
	            	$.each( postData, function( i, pD ) {
			  			result[pD.name] = pD.value;
			      	});

			      	result["model"] = model;
			      	result["act"] = "edit";

			      	$(this).dialog('close');

					$(".container").load("adm/"+model+"/edit",result);
	            },
	            "No": function () {
	                $(this).dialog('close');

	                model = "src"+model;

	                $(".container").load("/adm/"+model);
	            }
	        }
	    });

	});

	$('#table1 tr').on('click', function() {
		var ref = $(this).find("td").html();
    	$(this).toggleClass('selected');

    	console.log(model);

    	if (model.length > 8 && model=="students") { model = model.slice(3)};

    	$(".container").load("adm/edit"+model+"/"+ref+"/searchacc");
	});

    $("button[id^='back_']").click(function(){
    	model = $(this).attr("id").slice(5);
		$(".container").load("/adm/src"+model+"/");
	});
	
});
