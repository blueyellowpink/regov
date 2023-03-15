var head = null;

class node {
        constructor(val) {
            this.val = val;
            this.next = null;
        }
    }

function sortedMerge( a,  b)
{
    var result = null;

    if (a == null)
        return b;
    if (b == null)
        return a;

    /* Pick either a or b, and recur */
    if (a.val <= b.val) {
        result = a;
        result.next = sortedMerge(a.next, b);
    } else {
        result = b;
        result.next = sortedMerge(a, b.next);
    }
    return result;
}

function mergeSort( head ) {
    // Base case : if head is null
    if (head == null || head.next == null) {
        return head;
    }

    // get the middle of the list
    var middle = getMiddle(head);
    var nextOfMiddle = middle.next;

    // set the next of middle node to null
    middle.next = null;

    // Apply mergeSort on left list
    var left = mergeSort(head);


    var right = mergeSort(nextOfMiddle);


    var sortedList = sortedMerge(left, right);
    return sortedList;
}

function getMiddle( head) {
    if (head == null)
        return head;

    var slow = head, fast = head;

    while (fast.next != null && fast.next.next != null)
    {
        slow = slow.next;
        fast = fast.next.next;
    }
    return slow;
}

function insert(new_data) {
    /* allocate node */
    var new_node = new node(new_data);

    new_node.next = head;

    head = new_node;
}


function printList( head ) {
    const result = []
    while (head != null) {;
        result.push(head.val)
        head = head.next;
    }
    console.log('Output',result)
}

 

function inputHead (array) {
    for(let i = 0; i < array.length; i++){
        insert(array[i])
    }
}

console.log('Input', [-1,5,3,4,0])
inputHead([-1,5,3,4,0])

head = mergeSort(head);
printList(head);
