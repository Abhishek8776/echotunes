function confirmDelete(link) {
  event.preventDefault();
  Swal.fire({
    title: 'Are you sure?',
    text: link.getAttribute('data-confirm-message'),
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Yes, do it!'
  }).then((result) => {
    if (result.isConfirmed) {
      Swal.fire({ position: 'center', icon: 'success', title: 'Deleted', showConfirmButton: false, timer: 1500 })
      setTimeout(() => {
        window.location.href = link.href;
      }, 1500)
    }
  });
}
