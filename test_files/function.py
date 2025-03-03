from bmesh.types import BMVert, BMEdge, BMesh
from bpy import context
from bpy.types import Object, Panel
from bmesh import from_edit_mesh, update_edit_mesh
from typing import List, Tuple, Any, Set
from collections import defaultdict
from mathutils import Vector
from state_edge.stateEdges import StateEdge
from queue import PriorityQueue


# --------------------------- select the edge
obj: Object = context.object;
selectedEdges:List[BMEdge] = list()
selectedVertex:List[BMVert] =list()
bm: BMesh
length: int
if (obj.mode == 'EDIT'):
    bm = from_edit_mesh(obj.data)
    length = len(bm.edges)
    print(bm.edges)
    # for i, v in enumerate(bm.verts):
    # assert(length <=3), "there could be more than 3 Edges selected"
    for i in range(length):
        # print('Nicht selected edges: {}'.format(bm.edges[i]))
        if (bm.edges[i].select):
            print('selected edges: {}'.format(bm.edges[i]))
            selectedEdges.append(bm.edges[i])
            vertices = bm.edges[i].verts
            for j in range(len(vertices)):
                print("Index {}, values{}".format(j,vertices[j]))
                selectedVertex.append(vertices[j])
else:
    print("Object is not in edit mode.")

# ------------------- def graph

extendedNodes:PriorityQueue=PriorityQueue()

# -----------------------------



def edgeAngle(edge1: BMEdge, edge2: BMEdge) -> float:
    b: BMVert = set(edge1.verts).intersection(edge2.verts).pop()
    a: Vector = edge1.other_vert(b).co - b.co
    c: Vector = edge2.other_vert(b).co - b.co
    return a.angle(c);


def addEdges(values:StateEdge) -> None:
    extendedNodes.put(values)


def __deleteAllEdges() -> None:
    while not (extendedNodes.empty()):
        try:
            extendedNodes.get(False)
        except Exception:
            continue
        extendedNodes.task_done()

def __searchTheClosestValue(lengthValues: List[float], targetDistanceValue: float = 0.0) -> float:
    return lengthValues[min(range(len(lengthValues)), key=lambda i: abs(lengthValues[i] - targetDistanceValue))]

def __getDistanceBetweenEdges(currEdge: BMEdge, nextEdge: BMEdge) -> float:
    return abs(currEdge - nextEdge);

def __randListe( state: StateEdge = None) -> None:
    if(state is None):raise AssertionError('state ist NoneType')
    assert (len(state.children)>0), 'Children´s List is Empty'
    editedChildren: List[BMEdge] = None;
    children: List[StateEdge] = state.children[:]
    parentChildren: List[StateEdge] = state.parent.children[:] if(state.parent is not None) else None
    if (parentChildren is not None):
        editedChildren = children + parentChildren;
        for i in range(len(editedChildren)):
            addEdges(editedChildren[i])
    else:
        for j in range(len(children)):
            addEdges(children[j])
# --------------run----------------

def __excludeDuplicates() -> List[BMEdge]:
    i:int;
    currIndex:int
    indices:List[BMEdge] = list();
    if (len(selectedEdges)==1):
        return [selectedEdges[0].index]
    elif(len(selectedEdges)<1):
        print('the list ist empty')
    for i in range(len(selectedEdges)):
        indices.append(selectedEdges[i].index) # saves the indices
    return list(set(indices)) # removes the duplicates

def __checkNodeInStatus(action:StateEdge,currState:StateEdge) ->bool:
    assert ((currState is not None) and (action is not None)), 'it can not create children because the parent is NoneType';
    vertices: List[BMVert] = [vert for vert in action.action.verts]
    if (currState.node in vertices):
        return True;
    else:
        return False;

def __extractStatesParents(stateValue: StateEdge) -> List[BMEdge]:
    parents: List[BMEdge] = list()
    action: StateEdge = stateValue.parent;
    if (action is not None): parents.append(action.action);
    i: int = 0
    while (True):
        if (action.parent is None):
            break
        try:
            action = action.parent
            print('index:{}, action:{}'.format(i, action))
            parents.append(action.action)
        except Exception as e:
            print('[Exception] :', e)
        i += 1
    return parents

# --------------------
def __activateEdgesEDITMODE( edges:List[BMEdge]) -> None:
    # bm: BMesh = from_edit_mesh(self.__obj.data);
    i:int;
    currEdge:BMEdge;
    for i in range(len(edges[0])):
        #for j in range(len(edges[i])):
        print('index i:{}, edges:{}'.format(i,edges[0][i]))
        currEdge = edges[0][i];
        currEdge.select=True;
        bm.select_history.clear()
        bm.select_history.add(currEdge)
    update_edit_mesh(obj.data)
# --------- main

start: int = 0;
visited: List[int] = __excludeDuplicates() #[False] * len(self.__selectedEdges)
print(visited)
queue: BMEdge;
currEdge:BMEdge;
actions:List[BMEdge]= list();
__deleteAllEdges()
nextEdge:StateEdge;
status: StateEdge = StateEdge(parent=None, action=selectedEdges[0]);
# ------ create children-edges
status.createChildrenEdges();
# ------ save the status in EXTENDED NODES
__randListe(status);
while(True): # endlose Schleife
    #nextEdge = searchingPath.getScoreOfTheNextEdge();
    nextEdge = extendedNodes.get()
    #print('CUSTOMED NEXT EDGE {} vs  PRIORITY QUEUED EDGE{}'.format(nextEdge, nextEdge2[1].action))
    print('NEXT EDGE {}, NEXT VERTEX {}'.format(nextEdge.action,nextEdge.node))
    assert(nextEdge is not None), 'there is none edge!'
    if (nextEdge.action == status.goal):
        visited.append(nextEdge.action.index);
        selectedEdges.append(nextEdge.action)
        status = StateEdge(parent=status, action=nextEdge.action)
        #save the goal edge
        addEdges(status)
        print(' the goal EDGE {} was selected and added into SELECTED EDGES!'.format(nextEdge));
        actions.append(__extractStatesParents(status))
        break
    elif (nextEdge.action.index not in visited):
        start+=1;
        visited.append(nextEdge.action.index);
        selectedEdges.append(nextEdge.action)
        print('a new EDGE {} was selected and added into SELECTED EDGES!'.format(nextEdge));
    elif (nextEdge.action.index in visited):
        print('Jumping the code')
        continue
    # -------- check if parent node in current edge
    parentNode = __checkNodeInStatus(nextEdge, status)
    # ------- save the last node, action and children into the class itself
    if (parentNode is True):
        # ------- save the last node, action and children into the class itself
        status = StateEdge(status, nextEdge.action);
        # ------ calculate the score for the current edge
        status.calculateTheScore()
    else:
        # the last state will be saved into the priority queue
        addEdges(status);
        status = nextEdge
    # ------ create children-edges
    status.createChildrenEdges();
    # -------- save the status in EXTENDED NODES
    __randListe(status);
    print('a new OBJECT CLASS STATUS was added into the list of EXTENDED NODES!');
    start += 1;
    if (start == 70):
        actions.append(__extractStatesParents(status))
        #while not (extendedNodes.empty()):
            #actions.append(__extractStatesParents(extendedNodes.get()))
        break
for action in actions:
    print(action)
__activateEdgesEDITMODE(actions)



