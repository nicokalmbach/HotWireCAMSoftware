"use strict";

// Rein geometrische Anzeige; die geprüfte Schnittbahn kommt ausschließlich vom Planner.
function drawWorkspace(canvas, scene) {
    const ctx = canvas.getContext('2d');
    const {room, block, profiles, result, view, step, showNominal, access} = scene;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle='#101923';ctx.fillRect(0,0,canvas.width,canvas.height);
    ctx.font = '13px Segoe UI';
    const labels=[];
    function label(text, point, color='#d6e1e8') {
        if(text) labels.push({text,point,color});
    }
    function flushLabels() {
        for(const {text,point,color} of labels) {
            ctx.font = '13px Segoe UI';
            const width = ctx.measureText(text).width;
            const x = Math.max(8, Math.min(canvas.width-width-8, point[0]-width/2));
            const y = Math.max(18, Math.min(canvas.height-8, point[1]));
            ctx.fillStyle = '#101923e8'; ctx.fillRect(x-4,y-14,width+8,19);
            ctx.fillStyle = color; ctx.fillText(text,x,y);
        }
    }
    if (!room) {
        label('Maschinenmaße eingeben – der Arbeitsraum erscheint sofort.', [canvas.width/2,60]);
        flushLabels();
        return;
    }
    const {width, height, span} = room;
    const spatial = view === 'wire';
    const projection = (x,y,z) => spatial ? [x+z*.65, -y+z*.25] : [x,-y];
    const box = (w,h) => [[-w/2,0],[w/2,0],[w/2,h],[-w/2,h],[-w/2,0]];
    const roomBox = box(width,height);
    const bounds = [0,span].flatMap(z => roomBox.map(([x,y])=>projection(x,y,z)));
    // Ungültig platzierte Entwürfe sichtbar halten, statt sie am Canvasrand abzuschneiden.
    for (const profile of profiles) for (const contour of profile.contours) {
        for (const [x,y] of contour) bounds.push(projection(x,y,profile.z));
    }
    const xs=bounds.map(p=>p[0]), ys=bounds.map(p=>p[1]);
    const minX=Math.min(...xs), minY=Math.min(...ys);
    const scale=Math.min((canvas.width-210)/Math.max(1,Math.max(...xs)-minX),
                         (canvas.height-180)/Math.max(1,Math.max(...ys)-minY));
    const project=(x,y,z)=>{const p=projection(x,y,z);return [105+(p[0]-minX)*scale,65+(p[1]-minY)*scale];};
    function stroke(points, color, dashed=false, lineWidth=1) {
        if (!points.length) return;
        ctx.beginPath();ctx.strokeStyle=color;ctx.lineWidth=lineWidth;ctx.setLineDash(dashed?[5,5]:[]);
        points.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.stroke();ctx.setLineDash([]);
    }
    function face(points) {
        ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));
        ctx.closePath();ctx.fillStyle='#d8c67920';ctx.fill();
    }
    function marker(point, text, color) {
        ctx.beginPath();ctx.fillStyle=color;ctx.arc(...point,4,0,Math.PI*2);ctx.fill();
        label(text,[point[0],point[1]-12],color);
    }
    const fmt=v=>Number(v.toFixed(2)).toLocaleString('de-DE');
    function dimension(a,b,text,offset=[0,0]) {
        const p=project(...a).map((v,i)=>v+offset[i]), q=project(...b).map((v,i)=>v+offset[i]);
        stroke([project(...a),p], '#6a7781',true);stroke([project(...b),q], '#6a7781',true);
        stroke([p,q],'#b5c3cc');
        const dx=q[0]-p[0],dy=q[1]-p[1],length=Math.hypot(dx,dy);
        if(length>0) for(const point of [p,q]) stroke([[point[0]-dy/length*4,point[1]+dx/length*4],[point[0]+dy/length*4,point[1]-dx/length*4]],'#b5c3cc');
        label(text,[(p[0]+q[0])/2,(p[1]+q[1])/2-5]);
    }
    for (const z of spatial?[0,span]:[0]) {
        stroke(roomBox.map(([x,y])=>project(x,y,z)),'#708391');
        stroke([project(0,0,z),project(0,height,z)],'#51616c',true);
    }
    if(spatial) roomBox.slice(0,4).forEach(([x,y])=>stroke([project(x,y,0),project(x,y,span)],'#42525e'));
    if(block) {
        const {width:bw,height:bh,span:bs,z0,z1}=block;
        const blockBox=box(bw,bh);
        const ends=spatial?[z0,z1]:[0];
        if(spatial) {
            face([project(-bw/2,bh,z0),project(bw/2,bh,z0),project(bw/2,bh,z1),project(-bw/2,bh,z1)]);
            face([project(bw/2,0,z0),project(bw/2,bh,z0),project(bw/2,bh,z1),project(bw/2,0,z1)]);
            blockBox.slice(0,4).forEach(([x,y])=>stroke([project(x,y,z0),project(x,y,z1)],'#c9ba69'));
        }
        for(const z of ends) {face(blockBox.map(([x,y])=>project(x,y,z)));stroke(blockBox.map(([x,y])=>project(x,y,z)),'#e5cf80',false,2);}
        const front=spatial?z0:0;
        dimension([-bw/2,0,front],[bw/2,0,front],`Block X/U ${fmt(bw)} mm`,[0,32]);
        dimension([-bw/2,0,front],[-bw/2,bh,front],`Höhe ${fmt(bh)} mm`,[-50,0]);
        dimension([-width/2,height,0],[-bw/2,height,0],`X− ${fmt((width-bw)/2)} mm`,[0,-25]);
        dimension([bw/2,height,0],[width/2,height,0],`X+ ${fmt((width-bw)/2)} mm`,[0,-25]);
        dimension([width/2,bh,0],[width/2,height,0],`Oben ${fmt(height-bh)} mm`,[55,0]);
        if(spatial) {
            dimension([bw/2,0,z0],[bw/2,0,z1],`Blocklänge ${fmt(bs)} mm`,[0,54]);
            dimension([width/2,0,0],[width/2,0,z0],`XY-Abstand ${fmt(z0)} mm`,[0,85]);
            dimension([width/2,0,z1],[width/2,0,span],`UV-Abstand ${fmt(span-z1)} mm`,[0,85]);
        }
    }
    label('X/U = 0 · Y/V = 0',project(0,0,0));
    const visible=name=>spatial || view===name;
    for(const profile of profiles) {
        if(!visible(profile.name)) continue;
        profile.contours.forEach((points,index)=>stroke(points.map(([x,y])=>project(x,y,profile.z)),
            profile.name==='xy'?'#f0a45d':'#68c6ae',true,index===profile.selected?2:1));
    }
    // Vor der Berechnung sind nur Zugangspunkte sichtbar, keine vermeintlich gültige Schnittbahn.
    if(!result && block) for(const phase of ['entry','exit']) {
        const p=access?.[phase]; if(!p) continue;
        for(const [name,offset,z] of [['xy',0,block.z0],['uv',2,block.z1]]) if(visible(name)) {
            marker(project(p[offset],p[offset+1],z),`${phase==='entry'?'Einfahrt':'Ausfahrt'} ${name.toUpperCase()} · Entwurf`,phase==='entry'?'#79db98':'#dca2eb');
        }
    }
    if(!result) {flushLabels();return;}
    const {z_xy:z0,z_uv:z1}=result.room;
    const count=result.sections.length;
    const accessEnabled=scene.accessEnabled;
    const phases=accessEnabled?[[0,1,'#79db98'],[count-2,count-1,'#dca2eb']]:[];
    for(const [name,offset,z,axisZ,color] of [['xy',0,z0,0,'#f0a45d'],['uv',2,z1,span,'#68c6ae']]) {
        if(!visible(name)) continue;
        // Dünne Bahn an der Führung, kräftige tatsächliche Bahn auf der Blockstirnfläche.
        stroke(result.path.map(p=>project(p[offset],p[offset+1],axisZ)),'#586977',true);
        if(showNominal) stroke(result.nominal.map(p=>project(p[offset],p[offset+1],axisZ)),'#8fa1ad',true);
        stroke(result.sections.map(p=>project(p[offset],p[offset+1],z)),color,false,2.5);
        for(const [a,b,c] of phases) {
            const [p,q]=[a,b].map(i=>project(result.sections[i][offset],result.sections[i][offset+1],z));
            stroke([p,q],c,false,3);
            const dx=q[0]-p[0],dy=q[1]-p[1],length=Math.hypot(dx,dy);
            if(length>8) {
                const tip=[p[0]+dx*.35,p[1]+dy*.35];
                stroke([[tip[0]-dx/length*8-dy/length*5,tip[1]-dy/length*8+dx/length*5],tip,
                        [tip[0]-dx/length*8+dy/length*5,tip[1]-dy/length*8-dx/length*5]],c,false,2);
            }
        }
        const start=result.sections[0],end=result.sections.at(-1);
        const sameEnd=Math.hypot(start[offset]-end[offset],start[offset+1]-end[offset+1])<=1e-6;
        marker(project(start[offset],start[offset+1],z),`${sameEnd?(accessEnabled?'Start / Einfahrt + Ende / Ausfahrt':'Start + Ende'):(accessEnabled?'Start / Einfahrt':'Konturstart')} ${name.toUpperCase()}`,'#79db98');
        if(!sameEnd) marker(project(end[offset],end[offset+1],z),`Ende / ${accessEnabled?'Ausfahrt':'Konturende'} ${name.toUpperCase()}`,'#dca2eb');
        const p=result.sections[step];marker(project(p[offset],p[offset+1],z),'', '#ffffff');
    }
    if(spatial) {
        const every=Math.max(1,Math.ceil(result.path.length/24));
        result.path.forEach((p,i)=>{if(i%every===0)stroke([project(p[0],p[1],0),project(p[2],p[3],span)],'#354651');});
        const p=result.path[step];stroke([project(p[0],p[1],0),project(p[2],p[3],span)],'#ffffff',false,2.5);
    }
    flushLabels();
}
