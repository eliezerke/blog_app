const likeBtn = document.getElementById('likeBtn');
const likeCount = document.getElementById('likeCount');

if (likeBtn) {
  likeBtn.addEventListener('click', async () => {
    if (!IS_AUTH) {
      // Prompt sign in with a subtle shake
      likeBtn.style.animation = 'none';
      setTimeout(() => likeBtn.style.animation = '', 10);
      window.location.href = LOGIN_URL + '?next=' + encodeURIComponent(window.location.pathname);
      return;
    }
    try {
      const res = await fetch(`/api/like/${POST_ID}`, { method: 'POST' });
      const data = await res.json();
      likeCount.textContent = data.count;
      likeBtn.classList.toggle('liked', data.liked);
      likeBtn.classList.add('pop');
      setTimeout(() => likeBtn.classList.remove('pop'), 300);
    } catch (e) {
      console.error('Like failed:', e);
    }
  });
}

const commentInput = document.getElementById('commentInput');
const charCount = document.getElementById('charCount');

if (commentInput) {
  commentInput.addEventListener('input', () => {
    const len = commentInput.value.length;
    charCount.textContent = `${len} / 2000`;
    charCount.style.color = len > 1800 ? '#e05a5a' : '';
  });
}

async function submitComment(postId, parentId) {
  const inputId = parentId ? `replyInput-${parentId}` : 'commentInput';
  const input = document.getElementById(inputId);
  if (!input) return;
  const content = input.value.trim();
  if (!content) { input.focus(); return; }

  const btn = document.querySelector(parentId
    ? `#replyForm-${parentId} .btn-submit`
    : '#submitComment');
  const originalText = btn.textContent;
  btn.textContent = 'Posting…';
  btn.disabled = true;

  try {
    const form = new FormData();
    form.append('content', content);
    if (parentId) form.append('parent_id', parentId);

    const res = await fetch(`/api/comment/${postId}`, { method: 'POST', body: form });
    if (!res.ok) {
      const err = await res.json();
      showToast(err.error || 'Failed to post comment', 'error');
      return;
    }
    const comment = await res.json();
    input.value = '';
    if (charCount) charCount.textContent = '0 / 2000';

    // Inject new comment into DOM
    const html = buildCommentHTML(comment, postId);
    if (parentId) {
      // Add reply
      let repliesEl = document.getElementById(`replies-${parentId}`);
      if (!repliesEl) {
        repliesEl = document.createElement('div');
        repliesEl.className = 'replies';
        repliesEl.id = `replies-${parentId}`;
        document.querySelector(`#comment-${parentId} .comment-content`).appendChild(repliesEl);
      }
      repliesEl.insertAdjacentHTML('beforeend', html);
      toggleReplyForm(parentId);
    } else {
      const noComments = document.getElementById('noComments');
      if (noComments) noComments.remove();
      document.getElementById('commentsList').insertAdjacentHTML('afterbegin', html);
    }

    // Update badge
    const badge = document.getElementById('commentBadge');
    if (badge) badge.textContent = parseInt(badge.textContent) + 1;

    // Update reaction bar count
    const jumpBtn = document.querySelector('.comment-jump-btn span');
    if (jumpBtn) jumpBtn.textContent = parseInt(jumpBtn.textContent || '0') + 1;

  } finally {
    btn.textContent = originalText;
    btn.disabled = false;
  }
}

function buildCommentHTML(c, postId) {
  const avatar = c.author_avatar
    ? `<img src="${c.author_avatar}" alt="${escapeHtml(c.author_name)}"/>`
    : escapeHtml((c.author_name || 'U')[0].toUpperCase());
  const isReply = !!c.parent_id;
  const cls = isReply ? 'comment comment--reply' : 'comment';
  const avatarCls = isReply ? 'comment-avatar comment-avatar--sm' : 'comment-avatar';

  return `
<div class="${cls}" id="comment-${c.id}" data-id="${c.id}">
  <div class="${avatarCls}">${avatar}</div>
  <div class="comment-content">
    <div class="comment-header">
      <strong class="comment-author">${escapeHtml(c.author_name)}</strong>
      <span class="comment-date">${escapeHtml(c.created_at)}</span>
      <button class="comment-delete" onclick="deleteComment(${c.id})" title="Delete">✕</button>
    </div>
    <p class="comment-text">${escapeHtml(c.content)}</p>
    ${!isReply ? `
    <button class="reply-toggle" onclick="toggleReplyForm(${c.id})">Reply</button>
    <div class="reply-form" id="replyForm-${c.id}" style="display:none;">
      <textarea id="replyInput-${c.id}" placeholder="Write a reply…" rows="2" maxlength="2000"></textarea>
      <div class="reply-actions">
        <button class="btn-submit btn-submit--sm" onclick="submitComment(${postId}, ${c.id})">Reply</button>
        <button class="btn-cancel" onclick="toggleReplyForm(${c.id})">Cancel</button>
      </div>
    </div>` : ''}
  </div>
</div>`;
}

function escapeHtml(str) {
  const d = document.createElement('div');
  d.appendChild(document.createTextNode(String(str)));
  return d.innerHTML;
}

function toggleReplyForm(commentId) {
  const form = document.getElementById(`replyForm-${commentId}`);
  if (!form) return;
  const isOpen = form.style.display !== 'none';
  form.style.display = isOpen ? 'none' : 'block';
  if (!isOpen) {
    const ta = document.getElementById(`replyInput-${commentId}`);
    if (ta) ta.focus();
  }
}

async function deleteComment(commentId) {
  if (!confirm('Are you sure deleting the comment?')) return;
  try {
    const res = await fetch(`/api/comment/${commentId}`, { method: 'DELETE' });
    if (res.ok) {
      const el = document.getElementById(`comment-${commentId}`);
      if (el) {
        el.style.transition = 'opacity .3s';
        el.style.opacity = '0';
        setTimeout(() => el.remove(), 300);
      }
      const badge = document.getElementById('commentBadge');
      if (badge) badge.textContent = Math.max(0, parseInt(badge.textContent) - 1);
    }
  } catch (e) {
    showToast('Failed to delete comment', 'error');
  }
}

function sharePost() {
  if (navigator.share) {
    navigator.share({ title: document.title, url: window.location.href }).catch(() => {});
  } else {
    navigator.clipboard.writeText(window.location.href).then(() => {
      showToast('Link copied!', 'success');
    });
  }
}

function showToast(msg, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `flash flash--${type}`;
  toast.innerHTML = `<span>${msg}</span><button onclick="this.parentElement.remove()">✕</button>`;
  let container = document.querySelector('.flash-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'flash-container';
    document.body.appendChild(container);
  }
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.transition = 'opacity .4s';
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 400);
  }, 3500);
}

const reactionBar = document.getElementById('reactionBar');
if (reactionBar) {
  const sentinel = reactionBar.previousElementSibling;
  const stickyObserver = new IntersectionObserver(([e]) => {
    reactionBar.style.position = e.isIntersecting ? 'relative' : 'sticky';
    reactionBar.style.bottom = e.isIntersecting ? '' : '0';
  }, { threshold: 0 });
  if (sentinel) stickyObserver.observe(sentinel);
}
