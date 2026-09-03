self.onmessage = async (e) => {
  const { url = './compiled_lexicon_payload.json', chunkSize = 15000, dbName = 'LinguistHub_Core' } = e.data || {};

  const openDB = () => new Promise((resolve, reject) => {
    const req = indexedDB.open(dbName);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });

  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch payload`);
    
    const rawData = await res.json();
    const total = rawData.length;
    const db = await openDB();

    self.postMessage({ type: 'START', total });

    for (let i = 0; i < total; i += chunkSize) {
      const chunk = rawData.slice(i, i + chunkSize);
      
      await new Promise((resolve, reject) => {
        const tx = db.transaction('clusters', 'readwrite');
        const store = tx.objectStore('clusters');

        for (let j = 0; j < chunk.length; j++) {
          const item = chunk[j];
          const forms = item.f || {};
          store.put({
            word: item.w,
            pos: item.p || 'noun',
            definition: item.d || '',
            forms: {
              noun: forms.n || [],
              verb: forms.v || [],
              adjective: forms.j || [],
              adverb: forms.r || []
            },
            synonyms: item.s || [],
            antonyms: item.a || [],
            ar: item.ar || ''
          });
        }

        tx.oncomplete = () => resolve();
        tx.onerror = () => reject(tx.error);
      });

      const processed = Math.min(i + chunkSize, total);
      const pct = Math.round((processed / total) * 100);
      self.postMessage({ type: 'PROGRESS', processed, total, pct });
    }

    // Mark hydration complete in meta store
    await new Promise((resolve, reject) => {
      const tx = db.transaction('meta', 'readwrite');
      tx.objectStore('meta').put({ key: 'is_hydrated', value: true, timestamp: Date.now() });
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });

    self.postMessage({ type: 'COMPLETE' });
  } catch (err) {
    self.postMessage({ type: 'ERROR', message: err.message, stack: err.stack });
  }
};
