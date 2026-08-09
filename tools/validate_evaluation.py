import requests, time, json
base='http://127.0.0.1:8000/api/v1'
email=f'autotest_{int(time.time())}@example.com'
pw='Password1!'
print('register', email)
r=requests.post(base+'/auth/register', json={'full_name':'Auto Test','email':email,'password':pw})
print('reg', r.status_code)
r.raise_for_status()
L=requests.post(base+'/auth/login', data={'username':email,'password':pw,'grant_type':'password'})
L.raise_for_status()
token=L.json().get('access_token')
headers={'Authorization':f'Bearer {token}'}
results=[]
for interview_type in ['technical','hr','behavioral','system_design','mixed']:
    print('\n==',interview_type)
    create=requests.post(base+'/interview/sessions', json={'interview_type':interview_type}, headers=headers)
    print('create', create.status_code)
    data=create.json().get('data')
    q=data.get('question')
    qid=q.get('question_id')
    print('question_id', qid)
    # fetch question document from API
    qdoc_resp=requests.get(base+f'/interview/questions/{qid}')
    print('fetch question status', qdoc_resp.status_code)
    qdoc=qdoc_resp.json().get('data')
    core=[c.get('name') for c in (qdoc.get('core_concepts') or qdoc.get('expected_concepts') or [])]
    print('core concepts:', core)
    # submit a generic answer
    resp=requests.post(base+f"/interview/sessions/{data['session_id']}/turns", json={'raw_answer':'Sample generic answer for testing.'}, headers=headers)
    print('turn', resp.status_code)
    payload=resp.json().get('data')
    te=payload.get('turn_evaluation')
    print('turn_evaluation missing_concepts:', te.get('missing_concepts'))
    # compare sets
    core_set=set([s.lower() for s in core if s])
    missing_set=set([m.lower() for m in te.get('missing_concepts') or []])
    overlap=core_set & missing_set
    results.append({'type':interview_type,'question_id':qid,'core':core,'missing':te.get('missing_concepts'),'overlap':list(overlap)})
print('\nRESULTS:\n', json.dumps(results, indent=2))
