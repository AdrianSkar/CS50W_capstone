	
const hosts_internal = {
	'codesandbox': {
		"icon": 'https://codesandbox.io/favicon.ico',
		"embed": 'iframe',
		"attrs": {
			"allow": "accelerometer",
			"ambient-light-sensor": '',
			"encrypted-media": '',
			"gyroscope": "",
			"sandbox": "allow-forms allow-modals allow-popups allow-presentation allow-same-origin allow-scripts"
		},
		"url": function (url) {
			const suffix = '?autoresize=1&hidenavigation=1&theme=dark';
			return url + suffix;
		}
	},
	'youtube': {
		"attrs": {
			"frameborder": 0,
			"allow": "accelerometer",
			"autoplay": '',
			"encrypted-media": '',
			"gyroscope": '',
			"picture-in-picture": '',
			"allowfullscreen": ''
		},
		'fa_icon': ' <i class="fab fa-youtube fa-xs"></i>',
		'embed': 'iframe',
		'url': function (url) {
			/* Convert youtube regular urls to embed urls by capturing ids
				More at https://github.com/AdrianSkar/testField/blob/master/regex/youtube%20url%20to%20embed.js
			*/
			const yt_id_regex = /watch\?v=([\w-]{11})|youtu\.be\/([\w-]{11})/,
				yt_id = url.match(yt_id_regex)[1] ? url.match(yt_id_regex)[1] : url.match(yt_id_regex)[2];

			return `https://www.youtube.com/embed/${yt_id}`;
		}
	},
	'devdocs': {
		'embed': "iframe",
		'attrs': {
			"frameborder": 0,
			"allow": "fullscreen"
		}
	},
	'replit': {
		'embed': "iframe",
		'attrs': {
			"frameborder": 0,
			"allow": "fullscreen"
		},
		'url': function (url) {
			// Remove hash part (file) and add 'lite' suffix to be able to embed it, 
			// more at https://docs.replit.com/repls/embed
			const repl_regex = /(#.*)$/;
			return url.match(repl_regex) ? url.replace(repl_regex, '?lite=true') : url.concat('?lite=true');

			/// Embed according to docs but hides files and makes it difficult to navigate
			// return url.match(repl_regex) ? url.replace(repl_regex, '?lite=true&embed=true') : url.concat('?lite=true&embed=true');
		}
	},
	'gist': {
		"valid_url": function (url) {
			// Check for well formed gist url
			let regex = /https:\/\/gist.github.com\/.+\/[a-z0-9]{32}/;
			return url.match(regex);
		}
	},
	"codepen": {
		"embed": "iframe",
		"attrs": {
			"scrolling": "no",
			"frameborder": "no",
			"loading": "lazy",
			"allowtransparency": "true",
			"allowfullscreen": "true",
			"default-tab": "js,result"
		},
		"url": function (url) {
			let output = url.split('/'), suffix = "?theme-id=dark&default-tab=js,result";
			output.splice(4, 1, 'embed');
			return output.join('/') + suffix;
		}
	},
	"127.0.0.1": {
		"name": "localhost"
	}
};
// Make youtu.be behave as youtube 
hosts_internal['youtu.be'] = hosts_internal.youtube;

const languages = {
	'html': {
		'fa_icon_class': 'fa-html5',
		color: "#e44d26"
	},
	'css': {
		'fa_icon_class': 'fa-css3-alt',
		color: "#264de4"
	},
	'js': {
		'fa_icon_class': 'fa-js-square',
		color: "#efd81d"
	},
	'py': {
		'fa_icon_class': 'fa-python',
		color: "#3474a6"
	},
	'git': {
		'fa_icon_class': 'fa-git-alt',
		color: "#e94e31"
	},
};

// Insert language icons on language nav
function lang_nav(id, lang) {
	let ele = document.querySelector(`#${id}`);
	let fa_icon_tag = document.createElement('i');
	fa_icon_tag.classList.add('fab', `${languages[lang].fa_icon_class}`, 'fa-2x');
	ele.append(fa_icon_tag);
}

// Insert language icons before the selected element
function prepend_lang_icon(id, lang) {

	let ele = document.getElementById(id);

	let fa_icon_tag = document.createElement('i');
	fa_icon_tag.classList.add('fab', `${languages[lang].fa_icon_class}`, 'pe-2');
	fa_icon_tag.style.color = `${languages[lang].color}`;

	ele.prepend(fa_icon_tag);
}


document.addEventListener('DOMContentLoaded', function () {

	// Manage sites and examples links
	document.querySelectorAll('.link').forEach(link => {
		let external = true,
			internal = '';

		// Is within hosts_internal?
		for (const host in hosts_internal) {
			if ((link.href).match(host)) {
				external = false;
				link.host_name = host;
				let site = hosts_internal[host];
				
				// Insert fa_icon or icon if host has one
				if (site.fa_icon) {
					link.innerHTML += site.fa_icon;
				}
				else if (site.icon) {
					external = false;
					link.innerHTML += ` <img src="${site.icon}"`;
				}

			}
		}
		// Not within hosts_internal (external)
		if (external) {
			// Add external icon
			link.innerHTML += ' <i class="fas fa-external-link-alt fa-xxs" title="Will open in a new tab">';
			// Open in new tab with noreferrer
			Object.assign(link, {
				target: '_blank',
				rel: 'noopener noreferrer'
			});
		}
		else {
			// Add listener for internal loading
			link.addEventListener('click', event => load_internal(event, link));
		}
	});
});


function load_internal(event, link) {
	// Clear previous get params (gists)
	window.history.replaceState({}, document.title, location.pathname);

	const mc = document.querySelector('#mc'),
		host = hosts_internal[link.host_name];
	let frag = document.createDocumentFragment();

	// Reset main content
	mc.innerHTML = '';

	// Process the url if needed or assign the current one
	const url = host.url ? host.url(link.href) : link.href;

	// Prevent link default behavior if it's an embedabble match
	if (host.embed) event.preventDefault();
		
	let iframe = document.createElement('iframe');
	iframe.innerHTML = `Your browser does not support iframes but you can still find the content <a href=${link.href}>here</a>.`;

	// Apply common attrs
	Object.assign(iframe, {
		src: url,
		width: '100%',
		height: '100%',
		title: `${link.textContent}'s iframe from ${link.host_name}`
	});

	// Apply custom attrs
	for (const [key, value] of Object.entries(host.attrs)) {
		iframe.setAttribute(key, value);
	}

	// Add content 
	frag.append(iframe);
	mc.appendChild(frag);
}