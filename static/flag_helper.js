const newerPostId = document.querySelector('h2 a').href.split('/')[4];
const access_token = localStorage.getItem('access_token') || null;
const textarea = document.querySelector('#mod-flag-text');
textarea.value = textarea.value.trim(); // remove spaces from the vlaue

async function getModFlagOptionIdFromPost(post_id) {
  const resp = await fetch('/answers/' + post_id + '/flag_options?access_token=' + access_token);
  const data = await resp.json();
  const option_id = data.items.find(item => item.requires_comment).option_id;
  return option_id;
}

async function flagPostForModeratorAttention(post_id) {
  const postData = new FormData();
  postData.append('option_id', await getModFlagOptionIdFromPost(post_id));
  postData.append('access_token', localStorage.getItem('access_token'));
  postData.append('comment', document.querySelector('#mod-flag-text').value);
  await fetch('/answers/' + post_id + '/flag', {
      method: 'POST',
      body: postData
  });
  return 'success';
}

if (!access_token) {
    document.querySelector('.modal-body').innerHTML = '<span class="text-danger">You need to authenticate with Stack Exchange to flag this post!</span>';
    const modalButton = document.querySelector('#modflag-button')
    modalButton.id = 'se-auth-button';
    modalButton.className = 'btn btn-danger';
    modalButton.innerHTML = 'Authenticate and reload'
    modalButton.addEventListener('click', () => window.open('/authorization/redirect'));
}

document.querySelector('#modflag-button').addEventListener('click', async function() {
    const status = await flagPostForModeratorAttention(newerPostId);
    $('#flagModal').modal('hide');
    document.querySelector('#flagButton').innerHTML += ` <span class="text-success">(${status})</span>`;
});