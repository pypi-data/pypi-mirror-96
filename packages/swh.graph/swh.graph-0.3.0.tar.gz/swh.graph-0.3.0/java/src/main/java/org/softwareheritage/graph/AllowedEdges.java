package org.softwareheritage.graph;

import java.util.ArrayList;

/**
 * Edge restriction based on node types, used when visiting the graph.
 * <p>
 * <a href="https://docs.softwareheritage.org/devel/swh-model/data-model.html">Software Heritage
 * graph</a> contains multiple node types (contents, directories, revisions, ...) and restricting
 * the traversal to specific node types is necessary for many querying operations:
 * <a href="https://docs.softwareheritage.org/devel/swh-graph/use-cases.html">use cases</a>.
 *
 * @author The Software Heritage developers
 */

public class AllowedEdges {
    /**
     * 2D boolean matrix storing access rights for all combination of src/dst node types (first
     * dimension is source, second dimension is destination), when edge restriction is not enforced this
     * array is set to null for early bypass.
     */
    public boolean[][] restrictedTo;

    /**
     * Constructor.
     *
     * @param edgesFmt a formatted string describing <a href=
     *            "https://docs.softwareheritage.org/devel/swh-graph/api.html#terminology">allowed
     *            edges</a>
     */
    public AllowedEdges(String edgesFmt) {
        int nbNodeTypes = Node.Type.values().length;
        this.restrictedTo = new boolean[nbNodeTypes][nbNodeTypes];
        // Special values (null, empty, "*")
        if (edgesFmt == null || edgesFmt.isEmpty()) {
            return;
        }
        if (edgesFmt.equals("*")) {
            // Allows for quick bypass (with simple null check) when no edge restriction
            restrictedTo = null;
            return;
        }

        // Format: "src1:dst1,src2:dst2,[...]"
        String[] edgeTypes = edgesFmt.split(",");
        for (String edgeType : edgeTypes) {
            String[] nodeTypes = edgeType.split(":");
            if (nodeTypes.length != 2) {
                throw new IllegalArgumentException("Cannot parse edge type: " + edgeType);
            }

            ArrayList<Node.Type> srcTypes = Node.Type.parse(nodeTypes[0]);
            ArrayList<Node.Type> dstTypes = Node.Type.parse(nodeTypes[1]);
            for (Node.Type srcType : srcTypes) {
                for (Node.Type dstType : dstTypes) {
                    restrictedTo[srcType.ordinal()][dstType.ordinal()] = true;
                }
            }
        }
    }

    /**
     * Checks if a given edge can be followed during graph traversal.
     *
     * @param srcType edge source type
     * @param dstType edge destination type
     * @return true if allowed and false otherwise
     */
    public boolean isAllowed(Node.Type srcType, Node.Type dstType) {
        if (restrictedTo == null)
            return true;
        return restrictedTo[srcType.ordinal()][dstType.ordinal()];
    }
}
