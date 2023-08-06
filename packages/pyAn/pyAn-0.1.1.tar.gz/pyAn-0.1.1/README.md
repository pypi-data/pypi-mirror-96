pyAn - animation software for python. Does not use any other modules except turtle and math.
Commands
- startTurtle() - starts an animation.
- frame() - goes to the next frame.
- Obj class: Obj(args).
	- run() - draws the object.
	- Obj types: Obj([<object type>, other args]).
	-- 2d:
	--- ellipse: Obj(["ellipse", x, y, a, b, color, run])
	--- rectangle: Obj(["rectangle", x, y, w, h, color, run]).
	--- polyline: Obj(["polyline", [(x1,y1), (x2,y2), ...], color, run]).
	-- 3d:
	--- rect prism: Obj(["rect prism", x, y, z, w, h, d, color, run]).
	- color: tuple of (r, g, b).
	- run: attribute if you are going to automatically use run() on the object.
