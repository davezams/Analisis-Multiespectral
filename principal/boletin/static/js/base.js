$(document).ready(function(){
  /* Permite desplegar y recoger los diagnósticos de un paciente cuando
  un doctor hace click en cualquier de ellos
  */
  $(".list-group-item-heading").click(function(e){
    if ( $('div.active').attr('id') === $(this).parent().attr('id') ) {
      $(this).parent().removeClass("active");
      $(this).siblings().slideUp();
      return;
    }
    headingItems = $('#diags .list-group-item-heading');
    headingItems.parent().removeClass("active");
    hideShowItems = headingItems.siblings().slideUp();
    $(this).siblings().slideDown().parent().addClass("active");
    e.preventDefault();
  });

  /* Agrega una campo para subir imágenes
  */
  $("#add_file_entry").click(function(e){
    var n = $('#photos_input_list > input').length + 1;
    $('#photos_input_list').append("<input id=\"foto_diag_"+n+"\" name=\"foto_diag_"+n+"\" type=\"file\">");
    e.preventDefault();
  });

  /* Elimina el ultimo campo para subir imágenes
  */
  $("#del_file_entry").click(function(){
    $('#photos_input_list > input').last().remove();
  });

  /* Seleccionador de fechas
  */
  $(".datepicker").datepicker({
    yearRange:"1940:2017",	
    changeMonth: true,
    changeYear: true,
    showButtonPanel: true,
    dateFormat: "dd/mm/yy",
  });

  /* Muestra las imágenes de los diagnósticos cuando el usuario hace click
  */
  $(".photos_diag_div img").click(function(){
    id_dialogo = "#dialogo_" + $(this).attr('id');
    $(id_dialogo).dialog({
      modal: true,
      resizable: false,
      draggable: false,
      width: 'auto',
      closeOnEscape: true,
    });
  });
  $('#id_estatura').parent().after('<label>I.M.C.:</label>&nbsp;<span id="imc">0.00</span>');

  var calcular_imc = function() {
    var peso = +$('#id_peso').val();
    var estatura = +$('#id_estatura').val();

    var imc = 0.0;
    if ( peso > 0 && estatura > 0 ) {
      estatura /= 100;
      imc = peso / (estatura * estatura);
    }
    $('#imc').html(imc.toFixed(2));
  };
  $('#id_peso').blur(calcular_imc);
  $('#id_estatura').blur(calcular_imc);

});
