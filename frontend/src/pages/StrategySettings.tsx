import React from "react";
import { toast } from "react-hot-toast";

export default function StrategySettings() {
  async function runStrategy(kind: 'dca'|'breakout'|'grid') {
    try{
      const user_id = localStorage.getItem('user_id') || 'sterio068@mail.com';
      const r = await fetch('/api/strategy/run', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({kind, user_id})
      });
      const j = await r.json();
      if(j.ok || (j.result && j.result.ok)) toast.success(`已執行 ${kind}`);
      else toast(`${kind}：${j.error||'已返回'}`, {icon:'ℹ️'});
    }catch(e:any){
      toast.error('執行失敗：'+e.message);
    }
  }

  return (
    <>
      {/* 既有設定表單 ... */}
      <div className='mt-6 flex gap-2'>
        <button className='btn btn-primary' onClick={()=>runStrategy('dca')}>立即執行 DCA</button>
        <button className='btn' onClick={()=>runStrategy('breakout')}>立即執行 Breakout</button>
        <button className='btn' onClick={()=>runStrategy('grid')}>立即執行 Grid</button>
      </div>
    </>
  );
}
