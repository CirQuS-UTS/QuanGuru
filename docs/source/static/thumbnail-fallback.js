// (function(){
//   // Determine the correct _static path by inspecting an existing linked asset.
//   function getFallbackSrc(){
//     var links = document.querySelectorAll('link[href]');
//     for(var i=0;i<links.length;i++){
//       var href = links[i].href || '';
//       var idx = href.indexOf('/static/');
//       if(idx !== -1){
//         return href.slice(0, idx) + '/static/no_image.png';
//       }
//     }
//     // last resort: relative path
//     return 'static/no_image.png';
//   }

//   // A tiny SVG data URI used if no_image.png cannot be loaded.
//   var dataURI = 'data:image/svg+xml;utf8,' + encodeURIComponent(
//     '<svg xmlns="http://www.w3.org/2000/svg" width="320" height="180">' +
//       '<rect width="100%" height="100%" fill="#f3f4f6"/>' +
//       '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#6b7280" font-family="sans-serif" font-size="20">No image</text>' +
//     '</svg>'
//   );

//   document.addEventListener('DOMContentLoaded', function(){
//     var fallback = getFallbackSrc();
//     document.querySelectorAll('img').forEach(function(img){
//       // Respect an opt-out attribute if set on an image
//       if(img.dataset && img.dataset.noFallback) return;

//       // If image already missing, the error handler will fire. Attach handler now.
//       img.addEventListener('error', function handler(){
//         try{
//           // Avoid infinite loop if we already tried the fallback or a data URI
//           if(this.src === fallback || (this.src && this.src.indexOf('data:') === 0)) return;
//           // Stop this handler from running again for this image
//           this.removeEventListener('error', handler);

//           var self = this;
//           // If the static fallback fails, set an inline SVG as a final fallback
//           this.onerror = function(){
//             self.onerror = null;
//             self.src = dataURI;
//           };

//           // Try the static no_image.png in the docs _static directory
//           this.src = fallback;
//         }catch(e){
//           // If anything goes wrong, use the inline fallback
//           img.src = dataURI;
//         }
//       });
//     });

//     // Also attach handlers to any images that may be added later (e.g., lazy-loading galleries)
//     var obs = new MutationObserver(function(muts){
//       muts.forEach(function(m){
//         m.addedNodes && m.addedNodes.forEach(function(node){
//           if(node && node.nodeType === 1){
//             node.querySelectorAll && node.querySelectorAll('img').forEach(function(img){
//               if(img.dataset && img.dataset.noFallback) return;
//               // attach same handler logic as above
//               img.dispatchEvent(new Event('error'));
//             });
//           }
//         });
//       });
//     });
//     obs.observe(document.body, {childList:true, subtree:true});
//   });
// })();
