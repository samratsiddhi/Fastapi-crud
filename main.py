import json
import pathlib
from models import Track
from fastapi import FastAPI, Response, Depends
from database import TrackModel,engine
from sqlmodel import Session,select
from datetime import  datetime
from typing import List, Union

app = FastAPI()

# @app.on_event("startup")
# async def startup_event():
#     DATAFILE = pathlib.Path() /'tracks.json'
    
#     session = Session(engine)
    
#     stmt = select(TrackModel)
#     result = session.exec(stmt).first()
    
#     if result is None:
#         with open(DATAFILE, 'r') as f:
#             tracks = json.load(f)
#             for track in tracks:
                # track['last_play'] = datetime.strptime(track['last_play'], '%Y-%m-%d %H:%M:%S')
#                 data = TrackModel(**track)                
#                 session.add(data)
#         session.commit()
#     session.close()

def get_session():
    with Session(engine) as session:
        yield session
    
@app.get('/tracks/', response_model=List[Track])
def tracks(session: Session = Depends(get_session)):
        smtm = select(TrackModel)
        result = session.exec(smtm).all() 
        return result
       
@app.get('/tracks/{track_id}/',response_model=Union[Track,str])
def track(track_id:int, response: Response, session: Session = Depends(get_session)):
    track = session.get(TrackModel, track_id)
    if track is None:
        response.status_code=404
        return "Track not fount"        
    return track


@app.post("/tracks/", response_model= Track, status_code=201)
def create_track(track: TrackModel, session : Session = Depends(get_session)):
    track.last_play = datetime.strptime(track.last_play, '%Y-%m-%d %H:%M:%S')
    session.add(track)
    session.commit()
    session.refresh(track)
    return track

@app.put("/tracks/{track_id}",response_model=Union[Track,str])
def update_track(track_id:int, updated_track: Track ,response : Response,session: Session = Depends(get_session)):
    track = session.get(TrackModel, track_id)
    if track is None:
        response.status_code=404
        return "Track not found"   
          
    track_dict = updated_track.dict(exclude_unset=True)
    for key,val in track_dict.items():
        setattr(track, key,val)
        
    session.add(track)
    session.commit()
    session.refresh(track) 
    return track
        
@app.delete("/tracks/{track_id}")
def delete_track(track_id: int, response: Response, session: Session = Depends(get_session)):
    track = session.get(TrackModel, track_id)
    if track is None:
        response.status_code=404
        return "Track not found"  
    
    session.delete(track)
    session.commit()
    return Response(status_code=200)
    



