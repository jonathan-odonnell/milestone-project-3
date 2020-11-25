$("#sort")
  .children(".btn")
  .on("click", function () {
    let currentUrl = new URL(window.location);
    let sort = $(this).val();
    currentUrl.searchParams.set("sort", sort);
    window.location.replace(currentUrl);
  });

$("#filter").on("click", function () {
  let currentUrl = new URL(window.location);
  let selectedBrands = [];
  $("input[name='brands']:checked").each(function (i) {
    selectedBrands.push($(this).val());
  });
  let brands = selectedBrands.join(",");
  if (brands) {
    currentUrl.searchParams.set("brands", brands);
  }
  let price = $("input:radio:checked").val();
  if (price) {
    currentUrl.searchParams.set("price", price);
  }
  window.location.replace(currentUrl);
});

$("#clear-filters").on("click", function () {
  let currentUrl = new URL(window.location);
  currentUrl.searchParams.delete("price");
  currentUrl.searchParams.delete("brands");
  window.location.replace(currentUrl);
});
