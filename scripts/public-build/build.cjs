// Compile the browser application and render the public version of its actual footer.
const fs = require('node:fs');
const path = require('node:path');
const React = require('react');
const {renderToStaticMarkup} = require('react-dom/server');
const {transformSync} = require('esbuild');
const postcss = require('postcss');
const tailwind = require('tailwindcss');
process.chdir(path.resolve(__dirname, '../..'));
const html = fs.readFileSync('index.html','utf8');
const source = html.match(/<script type="text\/plain" id="app-source">([\s\S]*?)<\/script>/)[1];
const compile = code => transformSync(code, {loader:'tsx', target:'es2019', minify:true}).code;
fs.writeFileSync('programmes/site-assets/react-runtime.js', ['react/umd/react.production.min.js','react-dom/umd/react-dom.production.min.js'].map(file=>fs.readFileSync(path.join(__dirname,'node_modules',file),'utf8')).join('\n'));
const hooks = 'const {useState,useEffect,useRef,useMemo,useCallback,useContext,Fragment}=React;';
fs.writeFileSync('programmes/site-assets/public-app.js', compile('(function(){'+hooks+'\n'+source+'\n})();'));
let footer = source.slice(source.indexOf('const Footer: React.FC'),source.indexOf('// ==== components/EmailAlertsModal'));
footer = footer.replace(/<button[^>]*id="adminToggleBtn"[\s\S]*?<\/button>/,'<a href="/?open=admin" className="text-xs text-slate-400">Admin</a>');
footer = footer.replace(/<button contentEditable=\{false\} suppressContentEditableWarning type="button"\s+onClick=\{\(\) => window.dispatchEvent\(new CustomEvent\(\x27ng-open-program-finder\x27, \{detail:\{\}\}\)\)\}\s+className=("[^"]+")>([\s\S]*?)<\/button>/,'<a href="/programmes/" className=$1>$2</a>');
footer = footer.replace(/<button contentEditable=\{false\} suppressContentEditableWarning key=\{level\}[\s\S]*?className=("[^"]+")>([\s\S]*?)<\/button>/,'<a key={level} href={"/programmes/levels/"+level.toLowerCase()+".html"} className=$1>$2</a>');
const el=React.createElement;
const components={
  React,
  WhatsAppLink:({message,children,className})=>el('a',{href:'https://wa.me/601167701210?text='+encodeURIComponent(message),className},children),
  EditableImage:({src,alt,wrapperClassName,imgClassName})=>el('span',{className:wrapperClassName},el('img',{src,alt,className:imgClassName})),
  EditableText:({defaultText,linkPrefix,digitsOnly,className})=>linkPrefix?el('a',{className,href:linkPrefix+(digitsOnly?defaultText.replace(/\D/g,''):defaultText)},defaultText):el('span',{className},defaultText),
  registrationHref:()=>'/#/registerasstudent'
};
const Component=new Function(...Object.keys(components),compile(footer+'\nreturn Footer;'))(...Object.values(components));
const markup=renderToStaticMarkup(el(Component)).replaceAll('href="#','href="/#');
if(markup.includes('<button')) throw Error('Footer action missing a static destination');
fs.writeFileSync('programmes/site-assets/footer.fragment','<div id="ng-site-footer" class="ng-market">'+markup+'</div>');
const styles=html.slice(html.indexOf('.ng-market .ng-market-footer .ng-footer-consult'),html.indexOf('/*',html.indexOf('@media(prefers-reduced-motion:reduce) { .ng-market .ng-market-footer')));
const extras=styles.slice(0,styles.indexOf('transition:none!important; } }')+ 'transition:none!important; } }'.length);
postcss([tailwind({content:[{raw:markup,extension:'html'}],important:'#ng-site-footer',corePlugins:{preflight:false}})]).process('@tailwind utilities;', {from:undefined}).then(r=>{
  fs.writeFileSync('programmes/site-assets/site-footer.css', '#ng-site-footer{font-family:Montserrat,Arial,sans-serif;line-height:1.5}#ng-site-footer *{box-sizing:border-box;border-style:solid;border-width:0}#ng-site-footer :is(h2,h3,p){margin:0}#ng-site-footer a{text-decoration:none;color:inherit}#ng-site-footer img{display:block;max-width:100%}#ng-site-footer footer{margin:0;padding:0}'+r.css+'\n'+extras);
});

postcss([tailwind({content:[{raw:html,extension:'html'}]})]).process('@tailwind base; @tailwind components; @tailwind utilities;', {from:undefined}).then(r=>fs.writeFileSync('programmes/site-assets/public-utilities.css',r.css));
