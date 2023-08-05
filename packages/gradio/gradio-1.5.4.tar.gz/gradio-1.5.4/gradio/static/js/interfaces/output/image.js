const image_output = {
  html: `
    <div class="view_holder_parent">
    <div class="view_holders">
        <div class="saliency_holder hide">
          <canvas class="saliency"></canvas>
        </div>          
        <div class="output_image_holder hide">
          <img class="output_image">
        </div>
      </div>
    </div>      
    `,
  init: function(opts) {},
  output: function(data) {
    let io = this;
    let [img_data, coord] = data;
    this.target.find(".view_holder_parent").addClass("interface_box");
    this.target.find(".output_image_holder").removeClass("hide");
    img = this.target.find(".output_image").attr('src', img_data);
    if (coord.length) {
      img = img[0];
      img.onload = function() {
        var size = getObjectFitSize(true, img.width, img.height, img.naturalWidth, img.naturalHeight);
        var width = size.width;
        var height = size.height;
        io.target.find(".saliency_holder").removeClass("hide").html(`
          <canvas class="saliency" width=${width} height=${height}></canvas>`);
        var ctx = io.target.find(".saliency")[0].getContext('2d');
        ctx.lineWidth = 2;
        ctx.strokeStyle = 'red';
        ctx.font = '16px monospace';
        ctx.textBaseline = 'top';        
        for (let [label, left_x, top_y, right_x, bottom_y] of coord) {
          ctx.rect(left_x, top_y, right_x - left_x, bottom_y - top_y);
          ctx.fillText(label, left_x + 2, top_y + 2)
        }
        ctx.stroke();
      }
    }
  },
  clear: function() {
    this.target.find(".view_holder_parent").removeClass("interface_box");
    this.target.find(".output_image_holder").addClass("hide");
    this.target.find(".saliency_holder").addClass("hide");
    this.target.find(".output_image").attr('src', "")
  },
  load_example_preview: function(data) {
    return "<img src='"+data[0]+"' height=100>"
  },

}
