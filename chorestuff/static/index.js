(function($) {
  $.fn.message = function(category, message) {
    this.append($('<div class="alert alert-{{ category }} alert-dismissible text-center" role="alert"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true"><i class=\'fa fa-times\'></i></span></button><strong class=\'text-capitalize\'>{{ category }}!</strong> {{ message }}</div>'.replace('{{ category }}', category).replace('{{ category }}', category).replace('{{ message }}', message)));
  };
  return this;
})(jQuery)

$(document).ready(function() {
  $('.delete-tenant').click(function() {
    if (confirm('Delete tenant?')) {
      return true;
    }
    return false;
  });
});

