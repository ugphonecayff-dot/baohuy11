<!-- templates/index.html -->
<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Bot Admin</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5/dist/css/bootstrap.min.css" rel="stylesheet"></head><body>
<div class="container py-4">
<h2>📸 Logs ảnh thanh toán</h2><table class="table"><thead><tr><th>User ID</th><th>Caption</th><th>Gói</th><th>Status</th><th>Hành động</th></tr></thead><tbody>
{% for log in logs %}
<tr>
  <td>{{ log.user_id }}</td><td>{{ log.caption }}</td><td>{{ log.guess_package }}</td><td>{{ log.status }}</td>
  <td>
    {% if log.status=="pending" %}
    <form method="post" action="/send_key">
      <input type="hidden" name="user_id" value="{{ log.user_id }}">
      <input type="hidden" name="package" value="{{ log.guess_package }}">
      <button class="btn btn-success btn-sm">Send Key</button>
    </form>
    {% endif %}
  </td></tr>
{% endfor %}
</tbody></table>

<h2>🔑 Quản lý Keys</h2>
<form method="post" action="/add_keys">
<div class="mb-3"><label>Gói</label><input name="package" class="form-control"></div>
<div class="mb-3"><label>Keys (mỗi dòng)</label><textarea name="keys" class="form-control" rows="3"></textarea></div>
<button class="btn btn-primary">Add Keys</button>
</form>

<h2>📦 Tình trạng Keys</h2>
<ul>
{% for pkg, arr in keys.items() %}
<li><b>{{pkg}}</b>: {{ arr|length }} key</li>
{% endfor %}
</ul>
</div>
</body></html>
