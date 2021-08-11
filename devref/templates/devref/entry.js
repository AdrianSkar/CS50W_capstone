// Functionality that is specific to entry.html contents
// Loaded using 'include' because the functions need template data

document.addEventListener('DOMContentLoaded', function () {
	// Add content buttons
	document.querySelectorAll('.add_content').forEach(button => {
		button.addEventListener('click', post_content);
	});
	// Delete content buttons
	const delete_note_button = document.querySelector('button[name="note_delete"]');
	if (delete_note_button) {
		delete_note_button.addEventListener('click', function () {
			delete_note(event, "{{note_content.id}}");
		});
	}
	// Edit content buttons
	const edit_note_button = document.querySelector('button[name="note_edit"]');
	if (edit_note_button) {
		edit_note_button.addEventListener('click', function () {
			edit_note(event, "{{note_content.id}}");
		});
	}
	// Bookmark button
	document.querySelector('#bookmark').addEventListener('click', bookmark);

	// Enable Bootstrap tooltips
	const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
	const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
		return new bootstrap.Tooltip(tooltipTriggerEl);
	});

});

// Include entry name in page's title
document.title = `Devvy - {{ entry.name }}`;

function post_content(event) {

	const add_note = event.target.closest('#add_note'),
		add_site = event.target.closest('#add_site'),
		add_example = event.target.closest('#add_example'),
		mc = document.querySelector('#mc');

	if (add_note) {
		mc.innerHTML = `
		<h4> Add a note: </h4>
		<form action="{% url 'entry' entry.name %}" method="POST">
			{% csrf_token %}
			{{ note_form }}
			<input type="hidden" name="note" value="add_note" />
			<button type="submit" class="btn btn-sm btn-outline-primary">
			Submit</button>
		</form>
		`;
	}
	else if (add_site) {
		mc.innerHTML = `
		<h4> Add a site: </h4>
		<form action="{% url 'entry' entry.name %}" method="POST">
			{% csrf_token %}
			{{ site_form }}
			<input type="hidden" name="site" value="add_site" />
			<input type="hidden" name="link_type" value="PG" />
			<button type="submit" class="btn btn-sm btn-outline-primary">
			Submit</button>
		</form>
		`;
	}
	else if (add_example) {
		mc.innerHTML = `
		<h4> Add an example: </h4>
		<form action="{% url 'entry' entry.name %}" method="POST">
			{% csrf_token %}
			{{ site_form }}
			<input type="hidden" name="site" value="add_site" />
			<input type="hidden" name="link_type" value="EG" />
			<button type="submit" class="btn btn-sm btn-outline-primary">
			Submit</button>
		</form>
		`;
	}
}

function delete_note(event, note_id) {
	entry = "{{entry.name}}";
	fetch(`/entries/${entry}`, {
		method: 'PUT',
		body: JSON.stringify({
			note: note_id,
			delete: true
		})
	})
		.then(response => {
			// Load entry after deleting
			if (response.ok) window.location.href = response.url;
		})
		.catch(error => {
			console.log('Error:', error);
		});
}

// Edit note
function edit_note(event, note_id) {

	const note_title = document.querySelector('.note_title'),
		note_body = document.querySelector('.note_body'),
		button = event.target.closest('button');

	// If user clicks save:
	if (button.dataset.status === 'save') {
		let new_content = document.querySelector(`#edit_body_${note_id}`).value,
			new_title = document.querySelector(`#edit_title_${note_id}`).value;

		// Send new content
		update_note(event, note_id, new_title, new_content);

		// Update button
		button.innerHTML = '<i class="far fa-edit"></i> edit';
		button.dataset.status = 'edit';
	}
	// If user clicks edit:
	else {
		// Get current content from server (if not, double edits wouldn't be possible
		// as edited and saved data wouldn't be synced)
		fetch(`/note/${note_id}`)
			.then(response => response.json())
			.then(data => {
				// Fill fields to edit
				note_body.innerHTML = `<textarea id="edit_body_${note_id}" rows="4" cols="50">${data.content}</textarea>`;
				note_title.innerHTML = `<input id="edit_title_${note_id}" type="text" value="${data.title}"></input>`;

				// Update button
				button.innerHTML = '<i class="far fa-save"></i> save';
				button.dataset.status = 'save';
			})
			.catch(err => console.error(err));
	}
}

// Send new note content
function update_note(event, note_id, new_title, new_content) {
	let entry = "{{entry.name}}";
	// Send data
	fetch(`/entries/${entry}`, {
		method: 'PUT',
		body: JSON.stringify({
			note: note_id,
			edit: true,
			title: new_title,
			content: new_content
		})
	})
		.then(response => {
			// Update content
			fetch(`/note/${note_id}`)
				.then(response => response.json())
				.then(data => {
					document.querySelector('.note_title').textContent = data.title;
					document.querySelector('.note_body').textContent = data.content;
				})
				.catch(err => console.error(err));
		})
		.catch(error => console.log('Error:', error));
}

// Bookmark entry
function bookmark(event) {
	const entry_name = "{{entry.name}}",
		user_name = "{{ request.user.username }}",
		icon = document.getElementById('bookmark').firstChild;
	// Get bookmarkers
	fetch(`/bookmarkers/${entry_name}`)
		.then(response => response.json())
		.then(data => {
			let bookmarkers = data.bookmarkers;

			// If not a bookmarker
			if (!bookmarkers.some(el => el === user_name)) {
				// Bookmark it
				fetch(`/bookmarkers/${entry_name}`, {
					method: 'PUT',
					body: JSON.stringify({
						bookmark: true
					})
				})
					.then(data => {
						// Update icon and tooltip attrs
						icon.className = 'fas fa-bookmark';
						icon.parentElement.title = 'Unbookmark this entry';
						icon.parentElement.setAttribute('data-bs-original-title', 'Unbookmark this entry');
						icon.parentElement.setAttribute('aria-label', 'Unbookmark this entry');
					})
					;
			}
			else {
				// Un-bookmark it
				fetch(`/bookmarkers/${entry_name}`, {
					method: 'PUT',
					body: JSON.stringify({
						bookmark: false
					})
				})
					.then(data => {
						// Update icon and tooltip attrs
						icon.className = 'far fa-bookmark';
						icon.parentElement.title = 'Bookmark this entry';
						icon.parentElement.setAttribute('data-bs-original-title', 'Bookmark this entry');
						icon.parentElement.setAttribute('aria-label', 'Bookmark this entry');
					});
			}
		})
		.catch(error => console.error('Error:', error));
}

// Update menu placement message on load/resize
const def_content = function () {
	const menu_plc = window.innerWidth < 768 ? 'top' : 'left';
	if (document.querySelector('#no_content')) document.querySelector('#no_content').textContent = `There are no reference pages yet, but you can add one using the ${menu_plc} menu.`;
};
def_content();
window.onresize = def_content;